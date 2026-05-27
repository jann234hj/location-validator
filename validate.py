"""
Location validator — reads Excel, flags rows where Primary Location country != Working Location country.

Usage:
    python validate.py input.xlsx
    python validate.py input.xlsx -o flagged.xlsx
"""

import argparse, io, re, sys, unicodedata
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from openpyxl import load_workbook, Workbook
from openpyxl.styles import PatternFill, Font
import pycountry

POLISH_NAMES = {
    "polska": "Poland", "niemcy": "Germany", "ukraina": "Ukraine",
    "czechy": "Czech Republic", "slowacja": "Slovakia",
    "litwa": "Lithuania", "lotwa": "Latvia",
    "bialorus": "Belarus", "rosja": "Russia",
    "rumunia": "Romania", "wegry": "Hungary",
    "holandia": "Netherlands", "belgia": "Belgium", "francja": "France",
    "hiszpania": "Spain", "wlochy": "Italy",
    "wielka brytania": "United Kingdom", "anglia": "United Kingdom",
    "szwecja": "Sweden", "dania": "Denmark", "norwegia": "Norway",
    "finlandia": "Finland", "szwajcaria": "Switzerland",
    "chorwacja": "Croatia", "bulgaria": "Bulgaria", "grecja": "Greece",
    "turcja": "Turkey", "moldawia": "Moldova", "slowenia": "Slovenia",
    "kanada": "Canada", "indie": "India", "gruzja": "Georgia",
    "portugalia": "Portugal", "irlandia": "Ireland",
}

SKIP = {"remote", "home office", "home", "n/a", "na", "-", "", "tbd", "unknown",
        "not specified", "not set", "global", "various", "multiple", "hybrid", "flexible"}

PREFIXES = ["all ", "cala ", "whole ", "entire "]


def _norm(s):
    return re.sub(r"\s+", " ", s.strip().lower())

def _no_diacritics(s):
    s = s.replace("ł", "l").replace("Ł", "L")
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))

def _strip_prefix(s):
    for p in PREFIXES:
        if s.startswith(p): return s[len(p):].strip()
    return s

def _try_pycountry(token):
    for name in (token.title(), token):
        c = pycountry.countries.get(name=name)
        if c: return c.name
    c = pycountry.countries.get(alpha_2=token.upper())
    if c and len(token) == 2: return c.name
    c = pycountry.countries.get(alpha_3=token.upper())
    if c and len(token) == 3: return c.name
    return None

def _resolve(token):
    if not token or token in SKIP: return None
    r = _try_pycountry(token)
    if r: return r
    if token in POLISH_NAMES: return POLISH_NAMES[token]
    nd = _no_diacritics(token)
    if nd != token:
        if nd in POLISH_NAMES: return POLISH_NAMES[nd]
        r = _try_pycountry(nd)
        if r: return r
    if "," in token:
        for part in reversed(token.split(",")):
            r = _resolve(part.strip())
            if r: return r
    return None

def get_country(raw):
    if not raw or not isinstance(raw, str): return None
    s = _norm(raw)
    if s in SKIP: return None
    s = _strip_prefix(s)
    r = _resolve(s)
    if r: return r
    if "/" in s or ";" in s:
        cc = set()
        for part in re.split(r"[/;]", s):
            c = _resolve(_strip_prefix(part.strip()))
            if c: cc.add(c)
        if cc: return " / ".join(sorted(cc))
    for alias, c in POLISH_NAMES.items():
        if len(alias) > 2 and alias in s: return c
    return None

def find_col(headers, names):
    for i, h in enumerate(headers):
        if h and h.strip().lower() in [n.lower() for n in names]: return i
    return None

def run(input_path, output_path, primary_col, working_col, assignee_col):
    wb = load_workbook(input_path, read_only=True, data_only=True)
    rows = list(wb.active.iter_rows(values_only=True))
    if not rows: print("Empty spreadsheet."); return

    headers = [str(h).strip() if h else "" for h in rows[0]]
    pi = find_col(headers, [primary_col, "primary location", "lokalizacja"])
    wi = find_col(headers, [working_col, "working location", "lokalizacja pracy"])
    ai = find_col(headers, [assignee_col, "assignee", "name", "pracownik"])
    for name, idx in [("Primary Location", pi), ("Working Location", wi), ("Assignee", ai)]:
        if idx is None: print(f"ERROR: '{name}' column not found. Have: {headers}"); sys.exit(1)

    print(f"Processing {len(rows)-1} rows...")
    data = []
    for row in rows[1:]:
        a = str(row[ai]).strip() if row[ai] else ""
        p = str(row[pi]).strip() if row[pi] else ""
        w = str(row[wi]).strip() if row[wi] else ""
        if not a and not p and not w: continue
        data.append((a, p, w))

    results = []
    for a, p, w in data:
        pcc, wcc = get_country(p), get_country(w)
        if pcc is None or wcc is None:
            results.append((a, p, w, pcc, wcc, "UNRESOLVED", f"Can't parse: primary={pcc}, working={wcc}"))
        elif pcc == wcc:
            results.append((a, p, w, pcc, wcc, "MATCH", ""))
        else:
            results.append((a, p, w, pcc, wcc, "MISMATCH", f"{pcc} vs {wcc}"))

    m = sum(1 for r in results if r[5] == "MATCH")
    mm = sum(1 for r in results if r[5] == "MISMATCH")
    u = sum(1 for r in results if r[5] == "UNRESOLVED")
    print(f"\nTotal: {len(results)} | MATCH: {m} | MISMATCH: {mm} | UNRESOLVED: {u}\n")

    wb2 = Workbook(); ws = wb2.active; ws.title = "Results"
    fills = {"MATCH": PatternFill("solid", fgColor="C6EFCE"), "MISMATCH": PatternFill("solid", fgColor="FFC7CE"), "UNRESOLVED": PatternFill("solid", fgColor="FFEB9C")}
    for c, h in enumerate(["Assignee", "Primary (raw)", "Working (raw)", "Primary Country", "Working Country", "Verdict", "Note"], 1):
        ws.cell(1, c, h).font = Font(bold=True)
    for i, (a, p, w, pcc, wcc, v, n) in enumerate(results, 2):
        for c, val in enumerate([a, p, w, pcc or "???", wcc or "???", v, n], 1):
            ws.cell(i, c, val).fill = fills[v]
    wb2.save(output_path); print(f"Saved to: {output_path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Validate employee locations in Excel")
    ap.add_argument("input", help="Input .xlsx file")
    ap.add_argument("-o", "--output", default="flagged_locations.xlsx")
    ap.add_argument("--primary-col", default="Primary Location")
    ap.add_argument("--working-col", default="Working Location")
    ap.add_argument("--assignee-col", default="Assignee")
    args = ap.parse_args()
    if not Path(args.input).exists(): print(f"File not found: {args.input}"); sys.exit(1)
    run(args.input, args.output, args.primary_col, args.working_col, args.assignee_col)
