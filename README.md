# Location Validator

Validates employee location data in Excel files — flags rows where the **Primary Location** country doesn't match the **Working Location** country.

Built for HR/People teams dealing with messy, multilingual location data (Polish city names, mixed formats, abbreviations, etc).

## How it works

1. Reads an `.xlsx` file with columns: `Assignee`, `Primary Location`, `Working Location`
2. Resolves each location string to a country using multiple strategies:
   - ISO country codes (PL, UA, DE, UKR, POL, ...)
   - English country names
   - Polish country names (Polska, Niemcy, Ukraina, ...)
   - City-to-country dictionary (~150 cities across Europe)
   - pycountry library (fuzzy matching)
   - Nominatim geocoding (optional, cached to disk)
3. Compares countries and outputs a color-coded Excel file:
   - 🟢 **MATCH** — same country
   - 🔴 **MISMATCH** — different countries
   - 🟡 **UNRESOLVED** — couldn't determine one or both countries

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage
python validate.py employees.xlsx

# Custom output file
python validate.py employees.xlsx -o results.xlsx

# Skip online geocoding (faster, offline only)
python validate.py employees.xlsx --no-geocode

# Custom column names
python validate.py data.xlsx --primary-col "Home Location" --working-col "Office"
```

## Input format

Excel file with at minimum these columns (names are flexible):

| Assignee | Primary Location | Working Location |
|----------|-----------------|-----------------|
| Jan Kowalski | Warszawa, Polska | Kraków |
| Olena Boyko | Kyiv | Wrocław, PL |
| Hans Müller | München | Berlin, Germany |

## What it handles

- Polish and English country/city names (`Warszawa`, `Warsaw`, `Polska`, `Poland`)
- ISO codes (`PL`, `UA`, `DE`, `UKR`, `POL`)
- Diacritics (`Kraków` = `Krakow`, `Łódź` = `Lodz`)
- Prefixes (`All Poland`, `Cała Polska`)
- Multi-locations (`Poland / Ukraine`)
- Messy formatting (extra spaces, ALL CAPS, mixed case)
- Skip values (`Remote`, `Home Office`, `TBD`, `N/A`, `-`)

## Testing

```bash
# Run unit tests (46 cases)
pytest test_validate.py -v

# Generate mock data for testing
python generate_mock.py        # 1,000 rows
python generate_mock_10k.py    # 10,000 rows (requires geonamescache)
```

## Project structure

```
validate.py          — main validator script
locations.json       — city/country lookup data (editable)
test_validate.py     — unit tests
generate_mock.py     — mock data generator (1k rows)
generate_mock_10k.py — mock data generator (10k rows, real city names)
requirements.txt     — Python dependencies
```

## Extending

To add new cities or country name variants, edit `locations.json` — no code changes needed.
