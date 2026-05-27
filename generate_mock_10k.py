"""Generate a 10,000-row mock Excel file using real city names from geonamescache."""

import random
from openpyxl import Workbook
import geonamescache

random.seed(42)
gc = geonamescache.GeonamesCache()

# Build city pools by country from geonamescache (real cities, real names)
ALL_CITIES = gc.get_cities()
COUNTRIES_DATA = gc.get_countries()

def cities_for(cc):
    return [c["name"] for c in ALL_CITIES.values() if c["countrycode"] == cc]

PL_CITIES = cities_for("PL")  # ~347
UA_CITIES = cities_for("UA")  # ~263
DE_CITIES = cities_for("DE")  # ~1115
CZ_CITIES = cities_for("CZ")
SK_CITIES = cities_for("SK")
LT_CITIES = cities_for("LT")
RO_CITIES = cities_for("RO")
HU_CITIES = cities_for("HU")
NL_CITIES = cities_for("NL")
GB_CITIES = cities_for("GB")
FR_CITIES = cities_for("FR")
ES_CITIES = cities_for("ES")
IT_CITIES = cities_for("IT")

# Name pools
FIRST_PL = ["Jan", "Anna", "Piotr", "Katarzyna", "Michał", "Agnieszka", "Tomasz", "Magdalena",
            "Krzysztof", "Joanna", "Paweł", "Monika", "Marcin", "Dorota", "Łukasz", "Ewa",
            "Marek", "Justyna", "Grzegorz", "Beata", "Kamil", "Karolina", "Damian", "Natalia",
            "Robert", "Aleksandra", "Jakub", "Marta", "Wojciech", "Patrycja"]
LAST_PL = ["Kowalski", "Nowak", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński", "Lewandowski",
           "Zieliński", "Szymański", "Woźniak", "Dąbrowski", "Kozłowski", "Jankowski", "Mazur",
           "Kwiatkowski", "Krawczyk", "Piotrowski", "Grabowski", "Nowakowski", "Pawłowski",
           "Michalski", "Adamczyk", "Dudek", "Zając", "Wieczorek", "Jabłoński", "Król", "Majewski"]
FIRST_UA = ["Olena", "Andriy", "Iryna", "Dmytro", "Natalia", "Oleksandr", "Tetiana", "Viktor",
            "Oksana", "Serhiy", "Yulia", "Bohdan", "Kateryna", "Ivan", "Maryna", "Taras"]
LAST_UA = ["Shevchenko", "Bondarenko", "Kovalenko", "Boyko", "Tkachenko", "Kravchenko",
           "Marchenko", "Lysenko", "Melnyk", "Savchenko", "Moroz", "Ponomarenko", "Rudenko"]
FIRST_DE = ["Hans", "Monika", "Klaus", "Petra", "Stefan", "Sabine", "Wolfgang", "Claudia",
            "Jürgen", "Andrea", "Thomas", "Susanne", "Michael", "Birgit", "Frank", "Heike"]
LAST_DE = ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker",
           "Hoffmann", "Schäfer", "Koch", "Bauer", "Richter", "Klein", "Wolf", "Schröder"]
FIRST_OTHER = ["James", "Maria", "Carlos", "Sophie", "Marco", "Elena", "Pierre", "Ingrid",
               "Lars", "Cristina", "Alexandru", "Petra", "Tomáš", "Katarína", "Andrei"]
LAST_OTHER = ["Smith", "García", "Rossi", "Dubois", "Johansson", "Popescu", "Tóth", "Novák",
              "Van der Berg", "O'Brien", "Fernández", "Laurent", "Bergström", "Ionescu"]

# Country label variations
PL_LABELS = ["Poland", "Polska", "PL", "All Poland", "Cała Polska"]
UA_LABELS = ["Ukraine", "Ukraina", "UA", "All Ukraine"]
DE_LABELS = ["Germany", "Niemcy", "DE", "All Germany", "Deutschland"]
CZ_LABELS = ["Czech Republic", "Czechy", "CZ", "Czechia"]
OTHER_LABELS = {
    "SK": ["Slovakia", "Słowacja", "SK"],
    "LT": ["Lithuania", "Litwa", "LT"],
    "RO": ["Romania", "Rumunia", "RO"],
    "HU": ["Hungary", "Węgry", "HU"],
    "NL": ["Netherlands", "Holandia", "NL"],
    "GB": ["United Kingdom", "UK", "Anglia"],
    "FR": ["France", "Francja", "FR"],
    "ES": ["Spain", "Hiszpania", "ES"],
    "IT": ["Italy", "Włochy", "IT"],
}

UNRESOLVABLE = ["Remote", "Home Office", "N/A", "TBD", "Hybrid", "", "-", "Home",
                "Flexible", "Not set", "Unknown", "Global", "Various"]


def make_name(origin):
    if origin == "PL": return f"{random.choice(FIRST_PL)} {random.choice(LAST_PL)}"
    if origin == "UA": return f"{random.choice(FIRST_UA)} {random.choice(LAST_UA)}"
    if origin == "DE": return f"{random.choice(FIRST_DE)} {random.choice(LAST_DE)}"
    return f"{random.choice(FIRST_OTHER)} {random.choice(LAST_OTHER)}"


def make_loc(cities, labels):
    """Generate a messy location string."""
    style = random.choice(["city", "country", "city_country", "city_country_messy",
                           "caps", "spaces", "label_only"])
    city = random.choice(cities) if cities else "Unknown"
    label = random.choice(labels)

    if style == "city": return city
    if style == "country": return label
    if style == "city_country": return f"{city}, {label}"
    if style == "city_country_messy": return f"  {city} , {label}  "
    if style == "caps": return city.upper()
    if style == "spaces": return f"  {city}  "
    if style == "label_only": return label
    return city


def generate():
    wb = Workbook()
    ws = wb.active
    ws.title = "Employees"
    ws.append(["Assignee", "Primary Location", "Working Location"])

    rows = []

    # --- MATCHES (correct data) ---
    # ~5500 Polish employees
    for _ in range(5500):
        rows.append((make_name("PL"), make_loc(PL_CITIES, PL_LABELS), make_loc(PL_CITIES, PL_LABELS)))
    # ~1500 Ukrainian employees
    for _ in range(1500):
        rows.append((make_name("UA"), make_loc(UA_CITIES, UA_LABELS), make_loc(UA_CITIES, UA_LABELS)))
    # ~500 German employees
    for _ in range(500):
        rows.append((make_name("DE"), make_loc(DE_CITIES, DE_LABELS), make_loc(DE_CITIES, DE_LABELS)))
    # ~200 other European countries
    other_pools = [
        ("OTHER", CZ_CITIES, CZ_LABELS),
        ("OTHER", SK_CITIES, OTHER_LABELS["SK"]),
        ("OTHER", LT_CITIES, OTHER_LABELS["LT"]),
        ("OTHER", RO_CITIES, OTHER_LABELS["RO"]),
        ("OTHER", HU_CITIES, OTHER_LABELS["HU"]),
        ("OTHER", NL_CITIES, OTHER_LABELS["NL"]),
        ("OTHER", GB_CITIES, OTHER_LABELS["GB"]),
        ("OTHER", FR_CITIES, OTHER_LABELS["FR"]),
        ("OTHER", ES_CITIES, OTHER_LABELS["ES"]),
        ("OTHER", IT_CITIES, OTHER_LABELS["IT"]),
    ]
    for _ in range(200):
        origin, cities, labels = random.choice(other_pools)
        rows.append((make_name(origin), make_loc(cities, labels), make_loc(cities, labels)))

    # --- MISMATCHES (suspicious) ---
    # ~800 PL primary → UA working
    for _ in range(400):
        rows.append((make_name("PL"), make_loc(PL_CITIES, PL_LABELS), make_loc(UA_CITIES, UA_LABELS)))
    # ~300 UA primary → PL working
    for _ in range(300):
        rows.append((make_name("UA"), make_loc(UA_CITIES, UA_LABELS), make_loc(PL_CITIES, PL_LABELS)))
    # ~200 PL primary → DE working
    for _ in range(200):
        rows.append((make_name("PL"), make_loc(PL_CITIES, PL_LABELS), make_loc(DE_CITIES, DE_LABELS)))
    # ~100 DE primary → PL working
    for _ in range(100):
        rows.append((make_name("DE"), make_loc(DE_CITIES, DE_LABELS), make_loc(PL_CITIES, PL_LABELS)))
    # ~100 cross-European mismatches
    for _ in range(100):
        a, cities_a, labels_a = random.choice(other_pools)
        b, cities_b, labels_b = random.choice(other_pools)
        while labels_a == labels_b:
            b, cities_b, labels_b = random.choice(other_pools)
        rows.append((make_name("OTHER"), make_loc(cities_a, labels_a), make_loc(cities_b, labels_b)))

    # --- UNRESOLVED ---
    # ~500 with garbage/empty locations
    for _ in range(250):
        rows.append((make_name("PL"), make_loc(PL_CITIES, PL_LABELS), random.choice(UNRESOLVABLE)))
    for _ in range(150):
        rows.append((make_name("UA"), random.choice(UNRESOLVABLE), make_loc(UA_CITIES, UA_LABELS)))
    for _ in range(100):
        rows.append((make_name("OTHER"), random.choice(UNRESOLVABLE), random.choice(UNRESOLVABLE)))

    # Trim or pad to exactly 10,000
    random.shuffle(rows)
    rows = rows[:10000]

    for row in rows:
        ws.append(row)

    for col in ["A", "B", "C"]:
        ws.column_dimensions[col].width = 40

    wb.save("mock_input_10k.xlsx")
    print(f"Generated mock_input_10k.xlsx with {len(rows)} rows")
    print(f"  Cities used: PL={len(PL_CITIES)}, UA={len(UA_CITIES)}, DE={len(DE_CITIES)}")
    print(f"  Expected: ~7700 match, ~1100 mismatch, ~500 unresolved")


if __name__ == "__main__":
    generate()
