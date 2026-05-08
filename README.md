 # PRISMA-Oriented Screening Pipeline for a Semantic BEM Survey

   This repository contains the database-search and automated screening pipeline used to support the
 PRISMA-oriented component of a survey on semantic modelling for Building Energy Management (BEM). It processes
 exports from ACM Digital Library, IEEE Xplore, Lens, Scopus, and Web of Science.

   The repository documents the automated screening stages only. Manual abstract screening, full-text qualitative
 assessment, and complementary source identification are described in the survey methodology.

   ## Purpose

   The pipeline makes the automated database-screening stages transparent, auditable, and reproducible. It
 normalises titles, removes duplicate and non-English records, filters publication formats, and applies
 rule-based screening over bibliographic metadata.

   ## Main script

   ```text
   run_lens_new_only_pipeline.py
   ```

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

   ```bash
   pip install pandas openpyxl
   ```

   ## Run

   Place the database exports in `source_data/`, then run:

   ```bash
   python run_lens_new_only_pipeline.py
   ```

   Outputs are written to `export/`.

   ## Screening stages

   1. Title presence filtering.
   2. Title-based deduplication.
   3. Non-English record exclusion.
   4. Publication-format screening.
   5. Scope-based screening using title, abstract, and keywords.
   6. Rule-based title screening.

   ## Current run snapshot

   The survey run retrieved 34,216 raw records:

   ```text
   ACM Digital Library: 1,276
   IEEE Xplore:          402
   Lens:              20,247
   Scopus:            11,779
   Web of Science:       512
   Total:             34,216
   ```

   Automated screening results:

   ```text
   Title presence filter:          34,189 included /     27 excluded
   Deduplication:                  32,478 included /  1,711 excluded
   Language screening:             32,470 included /      8 excluded
   Publication-format screening:   28,554 included /  3,916 excluded
   Scope-based screening:           5,763 included / 22,791 excluded
   Rule-based title screening:      1,870 included /  3,893 excluded
   ```

   The 1,870 retained records were then assessed through manual abstract screening and full-text qualitative
 assessment.

   ## Relation to the survey corpus

   The PRISMA-oriented selection pipeline accounted for 71 ontology-relevant sources in the final survey corpus:

   ```text
   68 journal, conference, and workshop papers
   1 technical report
   2 books
   ```

   The final ontology-relevant set contains 149 references. The remaining 78 were identified through
 complementary procedures, including backward reference checking, forward citation tracing, manual venue
 searches, targeted retrieval of seminal ontology frameworks, and standards/project-related source tracing.


   ## Notes

   - This repository covers the automated screening stages only.
   - Manual screening and complementary source identification are not automated here.
   - Deduplication is based on normalised titles.
   - Screening rules are transparent and reproducible