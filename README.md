# PRISMA-Oriented Screening Pipeline

This repository contains a rule-based literature screening pipeline for PRISMA-style evidence gathering. It ingests exports from ACM, IEEE, Lens, Scopus, and Web of Science, normalizes and deduplicates records by title, then applies staged screening rules to produce included and excluded record sets at each step.

## What the pipeline does

The main script is [run_lens_new_only_pipeline.py](/C:/Users/mania/Desktop/prisma_oriented_screening_pipeline/run_lens_new_only_pipeline.py). It:

1. Loads CSV exports from `source_data/`.
2. Normalizes titles for consistent matching.
3. Removes blank-title records.
4. Deduplicates records by normalized title.
5. Screens out explicitly non-English records.
6. Screens out excluded publication formats.
7. Applies scope-based keyword rules across title, abstract, and keywords.
8. Applies a stricter title-based screening rule.
9. Writes Excel outputs for each included/excluded decision set into `export/`.

## Repository layout

```text
.
|-- run_lens_new_only_pipeline.py
|-- source_data/
|   |-- ACM.csv
|   |-- IEEE.csv
|   |-- Lens.csv
|   |-- Scopus.csv
|   `-- WOS.csv
`-- export/
```

## Requirements

- Python 3.10+
- `pandas`
- An Excel writer engine for `DataFrame.to_excel()`, typically `openpyxl`

Install dependencies with:

```bash
pip install pandas openpyxl
```

## Input data

Place the following CSV files in `source_data/`:

- `ACM.csv`
- `IEEE.csv`
- `Lens.csv`
- `Scopus.csv`
- `WOS.csv`

The script expects a `Title` column in every file and uses source-specific metadata fields when present, including abstract, keywords, language, document type, and year.

## How to run

From the repository root:

```bash
python run_lens_new_only_pipeline.py
```

The script creates the `export/` directory if it does not exist and overwrites matching output files from prior runs.

## Output files

The pipeline writes summary workbooks directly under `export/`:

- `source_stats.xlsx`
- `duplicates_per_source.xlsx`
- `screening_summary.xlsx`

It also writes included and excluded workbooks for each screening stage:

- `export/01_title_presence_filter/`
- `export/02_deduplication/`
- `export/03_language_screening/`
- `export/04_publication_format_screening/`
- `export/05_scope_based_screening/`
- `export/06_rule_based_title_screening/`

Each stage folder contains:

- `included.xlsx`
- `excluded.xlsx`

## Screening logic

The rules are encoded directly in the script as term lists and simple boolean conditions.

- Title presence filter: drops records with empty normalized titles.
- Deduplication: keeps the first record per normalized title using source priority.
- Language screening: excludes records with explicit non-English language metadata.
- Publication-format screening: excludes records such as dissertations, preprints, editorials, news items, retracted items, journal issues, and reports unless an allowed type is also present.
- Scope-based screening: looks for combinations of building, semantic, energy, and model terms across title, abstract, and keyword text.
- Rule-based title screening: keeps records whose titles show domain relevance plus semantic, model, review, or application signals.

## Current run snapshot

Running the script in this repository on May 8, 2026 produced:

- Title presence filter: included `34189`, excluded `27`
- Deduplication: included `32478`, excluded `1711`
- Language screening: included `32470`, excluded `8`
- Publication-format screening: included `28554`, excluded `3916`
- Scope-based screening: included `5763`, excluded `22791`
- Rule-based title screening: included `1870`, excluded `3893`

## Notes

- The script currently reads all source files from fixed paths under `source_data/`.
- Deduplication is title-based only; it does not currently use DOI or other identifiers.
- Output files are Excel workbooks, so large runs can take time and disk space.
