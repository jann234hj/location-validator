"""
Location validator — reads Excel, flags rows where Primary Location country != Working Location country.

Resolution order:
  1. ISO codes (alpha-2, alpha-3)
  2. English country names
  3. Polish country names
  4. City lookup (offline dict)
  5. pycountry fuzzy matching
  6. geopy/Nominatim geocoding (cached to disk, optional)

All lookup data loaded from locations.json (same folder).

Usage:
    pip install openpyxl pycountry geopy
    python validate.py input.xlsx
    python validate.py input.xlsx -o flagged.xlsx
    python validate.py input.xlsx --no-geocode
"""

import argparse, io, json, re, sys, time, unicodedata
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from openpyxl import load_workbook, Workbook
from openpyxl.styles import PatternFill, Font
import pycountry
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Load lookup tables from locations.json
_data = json.loads((Path(__file__).parent / "locations.json").read_text(encoding="utf-8"))
POLISH = _data["polish_names"]
ENGLISH = _data["english_names"]
ISO2 = _data["iso2"]
ISO3 = _data["iso3"]
CITIES = _data["cities"]
SKIP = set(_data["skip"])
PREFIXES = _data["prefixes"]

CACHE_FILE = Path(__file__).parent / ".geocache.json"
_geocoder = None
_geocache = {}
_geocode_enabled = True


def _load_cache():
    global _geocache
    if CACHE_FILE.exists():
        try: _geocache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception: _geocache = {}

def _save_cache():
    CACHE_FILE.write_text(json.dumps(_geocache, ensure_ascii=False, indent=2), encoding="utf-8")

def _get_geocoder():
    global _geocoder
    if _geocoder is None:
        _geocoder = Nominatim(user_agent="excel-location-validator", timeout=5)
    return _geocoder


def _nd(s):
    s = s.replace("ł", "l").replace("Ł", "L")
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))

def _try_pycountry(token):
    for name in (token.title(), token):
        c = pycountry.countries.get(name=name)
        if c: return c.name
    c = pycountry.countries.get(alpha_2=token.upper())
    if c and len(token) == 2: return c.name
    c = pycountry.countries.get(alpha_3=token.upper())
    if c and len(token) == 3: return c.name
    return None

def _try_geocode(token):
    if not _geocode_enabled: return None
    if token in _geocache: return _geocache[token]
    try:
        loc = _get_geocoder().geocode(token, language="en", exactly_one=True, addressdetails=True)
        time.sleep(1)
        if loc and "address" in loc.raw:
            country = loc.raw["address"].get("country")
            _geocache[token] = country
            return country
    except (GeocoderTimedOut, GeocoderUnavailable): pass
    except Exception: pass
    _geocache[token] = None
    return None

def _resolve(t):
    if not t or t in SKIP: return None
    up = t.upper()
    if len(t) == 2 and up in ISO2: return ISO2[up]
    if len(t) == 3 and up in ISO3: return ISO3[up]
    if t in ENGLISH: return ENGLISH[t]
    if t in POLISH: return POLISH[t]
    if t in CITIES: return CITIES[t]
    r = _try_pycountry(t)
    if r: return r
    nd = _nd(t)
    if nd != t:
        if nd in ENGLISH: return ENGLISH[nd]
        if nd in POLISH: return POLISH[nd]
        if nd in CITIES: return CITIES[nd]
        r = _try_pycountry(nd)
        if r: return r
    if "," in t:
        for part in reversed(t.split(",")):
            r = _resolve(part.strip())
            if r: return r
    r = _try_geocode(t)
    if r: return r
    return None

def get_country(raw):
    if not raw or not isinstance(raw, str): return None
    s = re.sub(r"\s+", " ", raw.strip().lower())
    if s in SKIP: return None
    s = _nd(s)
    for p in PREFIXES:
        if s.startswith(p): s = s[len(p):].strip(); break
    r = _resolve(s)
    if r: return r
    if "/" in s or ";" in s:
        cc = set()
        for part in re.split(r"[/;]", s):
            pt = part.strip()
            for p in PREFIXES:
                if pt.startswith(p): pt = pt[len(p):].strip(); break
            c = _resolve(pt)
            if c: cc.add(c)
        if cc: return " / ".join(sorted(cc))
    for alias, c in POLISH.items():
        if len(alias) > 2 and alias in s: return c
    return None


def _find_col(headers, names):
    for i, h in enumerate(headers):
        if h and h.strip().lower() in [n.lower() for n in names]: return i
    return None

def run(inp, out, pc, wc, ac):
    _load_cache()
    wb = load_workbook(inp, read_only=True, data_only=True)
    rows = list(wb.active.iter_rows(values_only=True))
    if not rows: print("Empty."); return

    hdrs = [str(h).strip() if h else "" for h in rows[0]]
    pi = _find_col(hdrs, [pc, "primary location", "lokalizacja"])
    wi = _find_col(hdrs, [wc, "working location", "lokalizacja pracy"])
    ai = _find_col(hdrs, [ac, "assignee", "name", "pracownik", "imię i nazwisko"])
    for n, idx in [("Primary Location", pi), ("Working Location", wi), ("Assignee", ai)]:
        if idx is None: print(f"ERROR: '{n}' column not found. Have: {hdrs}"); sys.exit(1)

    print(f"Columns: assignee='{hdrs[ai]}', primary='{hdrs[pi]}', working='{hdrs[wi]}'")
    print(f"Processing {len(rows)-1} rows...\n")

    data, locs = [], set()
    for row in rows[1:]:
        a = str(row[ai]).strip() if row[ai] else ""
        p = str(row[pi]).strip() if row[pi] else ""
        w = str(row[wi]).strip() if row[wi] else ""
        if not a and not p and not w: continue
        data.append((a, p, w)); locs.add(p); locs.add(w)

    print(f"Resolving {len(locs)} unique location strings...")
    resolved = {l: get_country(l) for l in locs}
    _save_cache()

    results = []
    for a, p, w in data:
        pcc, wcc = resolved[p], resolved[w]
        if pcc is None or wcc is None:
            results.append((a, p, w, pcc, wcc, "UNRESOLVED", f"Can't parse: primary={pcc}, working={wcc}"))
        elif set(pcc.split(" / ")) & set(wcc.split(" / ")):
            results.append((a, p, w, pcc, wcc, "MATCH", ""))
        else:
            results.append((a, p, w, pcc, wcc, "MISMATCH", f"{pcc} vs {wcc}"))

    m = sum(1 for r in results if r[5] == "MATCH")
    mm = sum(1 for r in results if r[5] == "MISMATCH")
    u = sum(1 for r in results if r[5] == "UNRESOLVED")
    print(f"\nTotal: {len(results)}  |  MATCH: {m}  |  MISMATCH: {mm}  |  UNRESOLVED: {u}\n")

    if mm:
        print("--- MISMATCHES ---")
        for a, p, w, pcc, wcc, v, n in results:
            if v == "MISMATCH": print(f"  {a}: '{p}' ({pcc}) vs '{w}' ({wcc})")
        print()
    if u:
        print("--- UNRESOLVED ---")
        for a, p, w, pcc, wcc, v, n in results:
            if v == "UNRESOLVED": print(f"  {a}: '{p}' vs '{w}' — {n}")
        print()

    wb2 = Workbook(); ws = wb2.active; ws.title = "Results"
    fills = {"MATCH": PatternFill("solid", fgColor="C6EFCE"), "MISMATCH": PatternFill("solid", fgColor="FFC7CE"), "UNRESOLVED": PatternFill("solid", fgColor="FFEB9C")}
    for c, h in enumerate(["Assignee", "Primary (raw)", "Working (raw)", "Primary Country", "Working Country", "Verdict", "Note"], 1):
        ws.cell(1, c, h).font = Font(bold=True)
    for i, (a, p, w, pcc, wcc, v, n) in enumerate(results, 2):
        for c, val in enumerate([a, p, w, pcc or "???", wcc or "???", v, n], 1):
            ws.cell(i, c, val).fill = fills[v]
    wb2.save(out); print(f"Saved to: {out}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Validate employee locations in Excel")
    ap.add_argument("input", help="Input .xlsx file")
    ap.add_argument("-o", "--output", default="flagged_locations.xlsx")
    ap.add_argument("--primary-col", default="Primary Location")
    ap.add_argument("--working-col", default="Working Location")
    ap.add_argument("--assignee-col", default="Assignee")
    ap.add_argument("--no-geocode", action="store_true", help="Skip online geocoding lookups")
    args = ap.parse_args()
    if not Path(args.input).exists(): print(f"File not found: {args.input}"); sys.exit(1)
    if args.no_geocode: _geocode_enabled = False
    run(args.input, args.output, args.primary_col, args.working_col, args.assignee_col)
