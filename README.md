# Location Validator

A Python tool for comparing location columns in Excel spreadsheets. Resolves messy, multilingual location strings to countries and flags mismatches.

## Problem

Large spreadsheets often contain location data entered inconsistently — city names in different languages, country abbreviations, mixed formats, typos. Manual comparison is slow and error-prone. This tool automates it.

## Features

- Resolves locations via ISO codes, English/Polish country names, city dictionaries, pycountry, and optional geocoding
- Handles diacritics, prefixes, multi-locations, ALL CAPS, extra whitespace
- Skips non-location values (Remote, Home Office, TBD, N/A)
- Outputs color-coded Excel (green = match, red = mismatch, yellow = unresolved)
- Lookup data stored in editable JSON — extend without touching code

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python validate.py input.xlsx
python validate.py input.xlsx -o results.xlsx
python validate.py input.xlsx --no-geocode
python validate.py input.xlsx --primary-col "Column A" --working-col "Column B"
```

Input Excel needs at least three columns — the tool auto-detects common names like `Assignee`, `Primary Location`, `Working Location` (configurable via CLI args).

## Testing

```bash
pytest test_validate.py -v
```

Mock data generators included for development (`generate_mock.py` for 1k rows, `generate_mock_10k.py` for 10k).

## Structure

```
validate.py          — main script
locations.json       — lookup data (cities, countries, ISO codes)
test_validate.py     — unit tests
generate_mock.py     — test data generator
generate_mock_10k.py — large-scale test data generator
requirements.txt     — dependencies
```

# Prompts

Side project. Four system prompts I happen to use — sharing in case any are interesting. No promises about what they do for you.

- **[00-teaser-nonclassical-logics.md](00-teaser-nonclassical-logics.md)** — excerpted from a preprint I'm currently finishing on verifying LLM reasoning under EU AI Act Art. 13. Headline result, runner skeleton, metric definitions. The rest is held back until the paper lands.
- **[01-structural-integrity.md](01-structural-integrity.md)** — structural lint over a nested JSON document.
- **[02-branching-graph.md](02-branching-graph.md)** — graph view of branching/conditional fields.
- **[03-semantic-ux.md](03-semantic-ux.md)** — review of the human-facing surface of the same document.

## Simplest possible use

Open the file, paste its content as the **system** message in any LLM chat. Paste whatever you want audited as the **user** message. Read the output.

That's it.
