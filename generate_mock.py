"""Generate a 1000-row mock Excel file with realistic messy location data."""

import random
from openpyxl import Workbook

random.seed(42)

# Realistic name pools
FIRST_NAMES_PL = ["Jan", "Anna", "Piotr", "Katarzyna", "Michał", "Agnieszka", "Tomasz", "Magdalena", "Krzysztof", "Joanna",
                  "Paweł", "Monika", "Marcin", "Dorota", "Łukasz", "Ewa", "Marek", "Justyna", "Grzegorz", "Beata"]
LAST_NAMES_PL = ["Kowalski", "Nowak", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński", "Lewandowski", "Zieliński",
                 "Szymański", "Woźniak", "Dąbrowski", "Kozłowski", "Jankowski", "Mazur", "Kwiatkowski",
                 "Krawczyk", "Piotrowski", "Grabowski", "Nowakowski", "Pawłowski"]
FIRST_NAMES_UA = ["Olena", "Andriy", "Iryna", "Dmytro", "Natalia", "Oleksandr", "Tetiana", "Viktor", "Oksana", "Serhiy"]
LAST_NAMES_UA = ["Shevchenko", "Bondarenko", "Kovalenko", "Boyko", "Tkachenko", "Kravchenko", "Marchenko",
                 "Lysenko", "Melnyk", "Savchenko"]
FIRST_NAMES_DE = ["Hans", "Monika", "Klaus", "Petra", "Stefan", "Sabine", "Wolfgang", "Claudia"]
LAST_NAMES_DE = ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker"]

# Location variations — messy on purpose
PL_CITIES = [
    "Warszawa", "Warsaw", "Kraków", "Krakow", "Wrocław", "Wroclaw", "Gdańsk", "Gdansk",
    "Poznań", "Poznan", "Łódź", "Lodz", "Katowice", "Szczecin", "Lublin", "Bydgoszcz",
    "Białystok", "Bialystok", "Rzeszów", "Rzeszow", "Toruń", "Zielona Góra", "Zielona Gora",
    "Opole", "Kielce", "Radom", "Gdynia", "Sopot", "Słupsk", "Koszalin", "Konin",
    "Tychy", "Bytom", "Rybnik", "Zakopane", "Piła", "Siedlce",
]
UA_CITIES = [
    "Kyiv", "Kiev", "Kijów", "Lviv", "Lwów", "Lwow", "Kharkiv", "Charków",
    "Odesa", "Odessa", "Dnipro", "Vinnytsia", "Winnica", "Ternopil", "Tarnopol",
    "Ivano-Frankivsk", "Lutsk", "Łuck", "Rivne", "Równe", "Uzhhorod",
    "Poltava", "Sumy", "Kherson", "Mykolaiv",
]
DE_CITIES = ["Berlin", "Munich", "München", "Monachium", "Hamburg", "Frankfurt", "Köln", "Kolonia",
             "Düsseldorf", "Stuttgart", "Dortmund", "Leipzig", "Dresden"]

PL_COUNTRY = ["Poland", "Polska", "PL", "All Poland", "Cała Polska", "All Poland"]
UA_COUNTRY = ["Ukraine", "Ukraina", "UA", "All Ukraine"]
DE_COUNTRY = ["Germany", "Niemcy", "DE", "Deutschland", "All Germany"]

MESSY_FORMATS = [
    lambda city, country: city,                              # just city
    lambda city, country: f"{city}, {country}",              # City, Country
    lambda city, country: country,                           # just country
    lambda city, country: f"  {city}  ",                     # extra spaces
    lambda city, country: city.upper(),                      # ALL CAPS
    lambda city, country: f"{city}, {country}  ",            # trailing space
]

UNRESOLVABLE = ["Remote", "Home Office", "N/A", "TBD", "Hybrid", "", "-", "Home", "Flexible"]


def make_name(origin):
    if origin == "PL":
        return f"{random.choice(FIRST_NAMES_PL)} {random.choice(LAST_NAMES_PL)}"
    elif origin == "UA":
        return f"{random.choice(FIRST_NAMES_UA)} {random.choice(LAST_NAMES_UA)}"
    else:
        return f"{random.choice(FIRST_NAMES_DE)} {random.choice(LAST_NAMES_DE)}"


def make_location(cities, countries):
    fmt = random.choice(MESSY_FORMATS)
    city = random.choice(cities)
    country = random.choice(countries)
    return fmt(city, country)


def generate():
    wb = Workbook()
    ws = wb.active
    ws.title = "Employees"
    ws.append(["Assignee", "Primary Location", "Working Location"])

    rows = []

    # ~600 legitimate Polish employees (primary PL, working PL) — MATCH
    for _ in range(600):
        rows.append((make_name("PL"), make_location(PL_CITIES, PL_COUNTRY), make_location(PL_CITIES, PL_COUNTRY)))

    # ~80 legitimate Ukrainian employees — MATCH
    for _ in range(80):
        rows.append((make_name("UA"), make_location(UA_CITIES, UA_COUNTRY), make_location(UA_CITIES, UA_COUNTRY)))

    # ~40 legitimate German employees — MATCH
    for _ in range(40):
        rows.append((make_name("DE"), make_location(DE_CITIES, DE_COUNTRY), make_location(DE_CITIES, DE_COUNTRY)))

    # ~100 MISMATCHES — people claiming wrong country
    # Polish primary, Ukrainian working
    for _ in range(40):
        rows.append((make_name("PL"), make_location(PL_CITIES, PL_COUNTRY), make_location(UA_CITIES, UA_COUNTRY)))
    # Ukrainian primary, Polish working
    for _ in range(30):
        rows.append((make_name("UA"), make_location(UA_CITIES, UA_COUNTRY), make_location(PL_CITIES, PL_COUNTRY)))
    # Polish primary, German working
    for _ in range(20):
        rows.append((make_name("PL"), make_location(PL_CITIES, PL_COUNTRY), make_location(DE_CITIES, DE_COUNTRY)))
    # German primary, Polish working
    for _ in range(10):
        rows.append((make_name("DE"), make_location(DE_CITIES, DE_COUNTRY), make_location(PL_CITIES, PL_COUNTRY)))

    # ~80 UNRESOLVED — one or both locations are garbage
    for _ in range(40):
        rows.append((make_name("PL"), make_location(PL_CITIES, PL_COUNTRY), random.choice(UNRESOLVABLE)))
    for _ in range(20):
        rows.append((make_name("PL"), random.choice(UNRESOLVABLE), make_location(PL_CITIES, PL_COUNTRY)))
    for _ in range(20):
        rows.append((make_name("UA"), random.choice(UNRESOLVABLE), random.choice(UNRESOLVABLE)))

    # ~50 tricky edge cases
    tricky = [
        ("Jan Podróżnik", "Zielona Gora, Poland", "All Ukraine"),
        ("Olena Traveller", "Kyiv", "Cała Polska"),
        ("Mixed Slash", "Poland", "Poland / Ukraine"),
        ("Anna Wszędzie", "Kraków, Polska", "All Poland"),
        ("Piotr Caps", "WARSZAWA", "POLAND"),
        ("Katarzyna Spaces", "  Wrocław  ", "  Polska  "),
        ("Empty Working", "Poznań", ""),
        ("Empty Both", "", ""),
        ("Dash Dash", "-", "-"),
        ("TBD Person", "TBD", "TBD"),
    ]
    for t in tricky:
        rows.append(t)
    # Fill remaining with random matches
    for _ in range(40):
        origin = random.choice(["PL", "UA", "DE"])
        if origin == "PL":
            rows.append((make_name("PL"), make_location(PL_CITIES, PL_COUNTRY), make_location(PL_CITIES, PL_COUNTRY)))
        elif origin == "UA":
            rows.append((make_name("UA"), make_location(UA_CITIES, UA_COUNTRY), make_location(UA_CITIES, UA_COUNTRY)))
        else:
            rows.append((make_name("DE"), make_location(DE_CITIES, DE_COUNTRY), make_location(DE_CITIES, DE_COUNTRY)))

    random.shuffle(rows)
    for row in rows:
        ws.append(row)

    # Auto-width
    for col in ["A", "B", "C"]:
        ws.column_dimensions[col].width = 35

    wb.save("mock_input.xlsx")
    print(f"Generated mock_input.xlsx with {len(rows)} rows")


if __name__ == "__main__":
    generate()
