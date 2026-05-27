import validate
validate._geocode_enabled = False

from validate import get_country

# --- Country names ---
def test_poland():          assert get_country("Poland") == "Poland"
def test_polska():          assert get_country("Polska") == "Poland"
def test_ukraine():         assert get_country("Ukraine") == "Ukraine"
def test_ukraina():         assert get_country("Ukraina") == "Ukraine"
def test_niemcy():          assert get_country("Niemcy") == "Germany"
def test_czechy():          assert get_country("Czechy") == "Czech Republic"
def test_code_pl():         assert get_country("PL") == "Poland"
def test_code_ua():         assert get_country("UA") == "Ukraine"
def test_code_de():         assert get_country("DE") == "Germany"

# --- pycountry exact ---
def test_pycountry_exact():     assert get_country("Poland") == "Poland"
def test_pycountry_iso2():      assert get_country("DE") == "Germany"
def test_pycountry_iso3():      assert get_country("UKR") == "Ukraine"

# --- Cities (offline dict covers common PL/UA/DE cities) ---
def test_warszawa():            assert get_country("Warszawa") == "Poland"
def test_krakow():              assert get_country("Krakow") == "Poland"
def test_kyiv():                assert get_country("Kyiv") == "Ukraine"
def test_lviv():                assert get_country("Lviv") == "Ukraine"
def test_berlin():              assert get_country("Berlin") == "Germany"
def test_uzhhorod():            assert get_country("Uzhhorod") == "Ukraine"
def test_warszawa_with_country():
    assert get_country("Warszawa, Poland") == "Poland"
    assert get_country("Warszawa, Polska") == "Poland"
def test_city_country():    assert get_country("Zielona Gora, Poland") == "Poland"
def test_krakow_polska():   assert get_country("Kraków, Polska") == "Poland"
def test_unknown_city_ok(): assert get_country("Smalltown, Poland") == "Poland"

# --- Prefixes ---
def test_all_poland():      assert get_country("All Poland") == "Poland"
def test_all_ukraine():     assert get_country("All Ukraine") == "Ukraine"
def test_cala_polska():     assert get_country("Cała Polska") == "Poland"

# --- Multi-location ---
def test_slash():
    r = get_country("Poland / Ukraine")
    assert "Poland" in r and "Ukraine" in r
def test_same_slash():      assert get_country("Poland / Poland") == "Poland"

# --- Whitespace/case ---
def test_spaces():          assert get_country("  Poland  ") == "Poland"
def test_upper():           assert get_country("POLAND") == "Poland"
def test_mixed():           assert get_country("pOlAnD") == "Poland"

# --- Unresolvable ---
def test_remote():          assert get_country("Remote") is None
def test_home():            assert get_country("Home Office") is None
def test_na():              assert get_country("N/A") is None
def test_empty():           assert get_country("") is None
def test_none():            assert get_country(None) is None
def test_dash():            assert get_country("-") is None
def test_tbd():             assert get_country("TBD") is None

# --- Substring fallback (Polish names) ---
def test_somewhere():       assert get_country("Somewhere in Polska") == "Poland"
def test_from_ukraine():    assert get_country("Working from Ukraina") == "Ukraine"

# --- Validation logic (end-to-end check) ---
def test_match():
    assert get_country("Zielona Gora, Poland") == get_country("All Poland")

def test_mismatch():
    assert get_country("Zielona Gora, Poland") != get_country("All Ukraine")

# --- Polish names coverage ---
def test_polish_holandia():  assert get_country("Holandia") == "Netherlands"
def test_polish_hiszpania(): assert get_country("Hiszpania") == "Spain"
def test_polish_wlochy():    assert get_country("Włochy") == "Italy"
def test_polish_szwecja():   assert get_country("Szwecja") == "Sweden"
def test_polish_wegry():     assert get_country("Węgry") == "Hungary"
