from pathlib import Path
import re
import unicodedata

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "source_data"
EXPORT_DIR = BASE_DIR / "export"

SOURCE_FILES = {
    "ACM": SOURCE_DIR / "ACM.csv",
    "IEEE": SOURCE_DIR / "IEEE.csv",
    "Lens_New": SOURCE_DIR / "Lens.csv",
    "Scopus": SOURCE_DIR / "Scopus.csv",
    "WOS": SOURCE_DIR / "WOS.csv",
}

METADATA_COLUMNS = {
    "abstract": ["Abstract"],
    "keywords": [
        "Author Keywords",
        "Keywords",
        "IEEE Terms",
        "Keywords Plus",
        "Fields of Study",
        "Mesh_Terms",
        "MeSH Terms",
    ],
    "language": ["Language"],
    "document_type": ["Document Type", "Publication Type", "Document Identifier"],
    "year": ["Publication Year", "Year", "Date Published"],
}

BUILDING_TERMS = [
    "building",
    "buildings",
    "smart building",
    "smart buildings",
    "built environment",
    "architecture",
    "construction",
    "hvac",
    "facility",
    "facilities",
    "home",
    "homes",
    "district",
    "urban planning",
    "ahu",
    "bim",
    "ifc",
    "commissioning",
    "domotic",
    "appliances",
]
SEMANTIC_TERMS = [
    "ontology",
    "ontologies",
    "semantic",
    "semantics",
    "linked data",
    "linked building data",
    "metadata",
    "ifcowl",
    "brick",
    "saref",
    "schema",
    "schemas",
    "interoperability",
    "knowledge representation",
    "knowledge graph",
    "owl",
    "rdf",
    "bot",
]
ENERGY_TERMS = [
    "energy",
    "thermal comfort",
    "comfort",
    "smart grid",
    "grid",
    "power",
    "demand response",
    "carbon",
    "heating",
    "cooling",
    "ventilation",
]
MODEL_TERMS = [
    "data model",
    "information model",
    "reference model",
    "domain model",
    "metadata schema",
    "ontology based",
    "semantic web",
]
ALLOWED_DOCUMENT_TYPE_TERMS = [
    "article",
    "review",
    "conference",
    "proceedings paper",
    "paper",
    "chapter",
]
EXCLUDED_DOCUMENT_TYPE_TERMS = [
    "dissertation",
    "preprint",
    "editorial",
    "news item",
    "retracted",
    "journal issue",
    "report",
]
SEMANTIC_TITLE_TERMS = [
    "ontology",
    "ontologies",
    "ontological",
    "semantic",
    "semantics",
    "linked data",
    "metadata",
    "schema",
    "schemas",
    "interoperability",
    "ifcowl",
    "brick",
    "saref",
    "owl",
    "rdf",
    "bot",
]
DOMAIN_TITLE_TERMS = [
    "building",
    "buildings",
    "smart building",
    "smart buildings",
    "building automation",
    "building energy",
    "built environment",
    "architecture",
    "aec",
    "construction",
    "hvac",
    "facility",
    "facilities",
    "home",
    "homes",
    "district",
    "urban",
    "bim",
    "ifc",
    "energy",
    "thermal comfort",
    "heating",
    "cooling",
    "ventilation",
    "grid",
    "power",
    "demand response",
    "commissioning",
    "automation",
    "smart appliances",
]
MODEL_TITLE_TERMS = [
    "data model",
    "information model",
    "domain model",
    "reference model",
    "information modeling",
    "semantic web",
    "knowledge representation",
    "digital twin",
]
REVIEW_TITLE_TERMS = [
    "review",
    "survey",
    "state of the art",
    "literature overview",
    "systematic comparison",
]
APPLICATION_TITLE_TERMS = [
    "optimization",
    "decision making",
    "decision-making",
    "data driven",
    "service oriented architecture",
    "hybrid inference",
    "benchmarking",
    "operations",
    "operation",
    "management",
    "analytics",
]


def normalize_title(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def combine_columns(df: pd.DataFrame, column_names: list[str]) -> pd.Series:
    combined = pd.Series([""] * len(df), index=df.index, dtype="object")
    for column_name in column_names:
        if column_name in df.columns:
            combined = (
                combined.fillna("") + " " + df[column_name].fillna("").astype(str)
            ).str.strip()
    return combined


def merge_unique_text(values, sep=" | "):
    merged_values = []
    seen_values = set()
    for value in values:
        if pd.isna(value):
            continue
        normalized_value = str(value).strip()
        if not normalized_value or normalized_value in seen_values:
            continue
        seen_values.add(normalized_value)
        merged_values.append(normalized_value)
    return sep.join(merged_values)


def parse_year(value: object):
    if pd.isna(value):
        return pd.NA
    text = str(value).strip()
    if not text:
        return pd.NA
    match = re.search(r"(19|20)\d{2}", text)
    if not match:
        return pd.NA
    return int(match.group(0))


def has_any_term(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def export_pair(
    step_no: str,
    step_slug: str,
    included_df: pd.DataFrame,
    excluded_df: pd.DataFrame,
) -> None:
    step_dir = EXPORT_DIR / f"{step_no}_{step_slug}"
    step_dir.mkdir(parents=True, exist_ok=True)
    included_df.to_excel(step_dir / "included.xlsx", index=False)
    excluded_df.to_excel(step_dir / "excluded.xlsx", index=False)


def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    source_rows = []
    title_frames = []
    screening_frames = []

    for source_name, path in SOURCE_FILES.items():
        df = pd.read_csv(path)

        title_working = df[["Title"]].copy()
        title_working["source_database"] = source_name
        title_working["original_title"] = title_working["Title"]
        title_working["normalized_title"] = title_working["Title"].apply(normalize_title)
        title_working = title_working[
            ["source_database", "original_title", "normalized_title"]
        ]
        title_frames.append(title_working)

        source_rows.append(
            {
                "source_database": source_name,
                "file_name": path.name,
                "raw_records": len(title_working),
                "usable_title_records": int(
                    (title_working["normalized_title"] != "").sum()
                ),
                "blank_title_records": int(
                    (title_working["normalized_title"] == "").sum()
                ),
            }
        )

        year_text = combine_columns(df, METADATA_COLUMNS["year"])
        screening_frames.append(
            pd.DataFrame(
                {
                    "source_database": source_name,
                    "original_title": df["Title"],
                    "normalized_title": df["Title"].apply(normalize_title),
                    "abstract_text": combine_columns(df, METADATA_COLUMNS["abstract"]),
                    "keyword_text": combine_columns(df, METADATA_COLUMNS["keywords"]),
                    "language_text": combine_columns(df, METADATA_COLUMNS["language"]),
                    "document_type_text": combine_columns(
                        df, METADATA_COLUMNS["document_type"]
                    ),
                    "year_text": year_text,
                    "publication_year": year_text.apply(parse_year),
                }
            )
        )

    source_stats_df = (
        pd.DataFrame(source_rows)
        .sort_values("source_database")
        .reset_index(drop=True)
    )
    source_stats_df.to_excel(EXPORT_DIR / "source_stats.xlsx", index=False)

    merged_raw_df = pd.concat(title_frames, ignore_index=True)
    blank_title_df = merged_raw_df[merged_raw_df["normalized_title"] == ""].copy()
    usable_title_df = merged_raw_df[merged_raw_df["normalized_title"] != ""].copy()
    export_pair("01", "title_presence_filter", usable_title_df, blank_title_df)

    dedup_base_df = pd.concat(screening_frames, ignore_index=True)
    dedup_base_df = dedup_base_df[dedup_base_df["normalized_title"] != ""].copy()
    dedup_base_df["source_priority"] = dedup_base_df["source_database"].map(
        {name: idx for idx, name in enumerate(SOURCE_FILES.keys())}
    )
    dedup_base_df["source_row_number"] = dedup_base_df.groupby(
        "source_database"
    ).cumcount()
    dedup_base_df = dedup_base_df.sort_values(
        ["normalized_title", "source_priority", "source_row_number"]
    ).reset_index(drop=True)
    dedup_base_df["removed_as_duplicate"] = dedup_base_df.duplicated(
        subset=["normalized_title"], keep="first"
    )
    dedup_included_df = dedup_base_df[~dedup_base_df["removed_as_duplicate"]].copy()
    dedup_excluded_df = dedup_base_df[dedup_base_df["removed_as_duplicate"]].copy()
    export_pair("02", "deduplication", dedup_included_df, dedup_excluded_df)

    duplicates_per_source_df = (
        dedup_base_df.groupby("source_database", as_index=False)["removed_as_duplicate"]
        .sum()
        .rename(columns={"removed_as_duplicate": "duplicates_removed"})
        .sort_values("source_database")
        .reset_index(drop=True)
    )
    duplicates_per_source_df.to_excel(
        EXPORT_DIR / "duplicates_per_source.xlsx", index=False
    )

    aggregated_df = (
        dedup_included_df.groupby("normalized_title", as_index=False)
        .agg(
            representative_title=("original_title", lambda values: merge_unique_text(values, " || ")),
            combined_abstract=("abstract_text", lambda values: merge_unique_text(values, " ")),
            combined_keywords=("keyword_text", lambda values: merge_unique_text(values, " ")),
            combined_language=("language_text", lambda values: merge_unique_text(values, " | ")),
            combined_document_type=("document_type_text", lambda values: merge_unique_text(values, " | ")),
            source_databases=("source_database", lambda values: merge_unique_text(values, " | ")),
            source_year_values=("year_text", lambda values: merge_unique_text(values, " | ")),
            publication_year=("publication_year", "max"),
        )
        .sort_values("normalized_title")
        .reset_index(drop=True)
    )

    aggregated_df["search_text"] = (
        aggregated_df["representative_title"].fillna("")
        + " "
        + aggregated_df["combined_abstract"].fillna("")
        + " "
        + aggregated_df["combined_keywords"].fillna("")
    ).apply(normalize_title)
    aggregated_df["language_text_normalized"] = aggregated_df["combined_language"].apply(
        normalize_title
    )
    aggregated_df["document_type_text_normalized"] = aggregated_df[
        "combined_document_type"
    ].apply(normalize_title)

    aggregated_df["is_non_english_explicit"] = (
        aggregated_df["language_text_normalized"].ne("")
        & ~aggregated_df["language_text_normalized"].str.contains(
            "english", regex=False
        )
    )
    language_included_df = aggregated_df[~aggregated_df["is_non_english_explicit"]].copy()
    language_excluded_df = aggregated_df[aggregated_df["is_non_english_explicit"]].copy()
    export_pair("03", "language_screening", language_included_df, language_excluded_df)

    language_included_df["has_allowed_document_type"] = language_included_df[
        "document_type_text_normalized"
    ].apply(lambda value: has_any_term(value, ALLOWED_DOCUMENT_TYPE_TERMS))
    language_included_df["has_excluded_document_type"] = language_included_df[
        "document_type_text_normalized"
    ].apply(lambda value: has_any_term(value, EXCLUDED_DOCUMENT_TYPE_TERMS))
    language_included_df["is_excluded_publication_format"] = (
        language_included_df["has_excluded_document_type"]
        & ~language_included_df["has_allowed_document_type"]
    )
    publication_included_df = language_included_df[
        ~language_included_df["is_excluded_publication_format"]
    ].copy()
    publication_excluded_df = language_included_df[
        language_included_df["is_excluded_publication_format"]
    ].copy()
    export_pair(
        "04",
        "publication_format_screening",
        publication_included_df,
        publication_excluded_df,
    )

    publication_included_df["has_building_term"] = publication_included_df[
        "search_text"
    ].apply(lambda value: has_any_term(value, BUILDING_TERMS))
    publication_included_df["has_semantic_term"] = publication_included_df[
        "search_text"
    ].apply(lambda value: has_any_term(value, SEMANTIC_TERMS))
    publication_included_df["has_energy_term"] = publication_included_df[
        "search_text"
    ].apply(lambda value: has_any_term(value, ENERGY_TERMS))
    publication_included_df["has_model_term"] = publication_included_df[
        "search_text"
    ].apply(lambda value: has_any_term(value, MODEL_TERMS))
    publication_included_df["passes_scope_prescreen"] = (
        (
            publication_included_df["has_building_term"]
            & publication_included_df["has_semantic_term"]
        )
        | (
            publication_included_df["has_building_term"]
            & publication_included_df["has_model_term"]
        )
        | (
            publication_included_df["has_energy_term"]
            & publication_included_df["has_semantic_term"]
        )
        | (
            publication_included_df["has_building_term"]
            & publication_included_df["has_energy_term"]
        )
    )
    scope_included_df = publication_included_df[
        publication_included_df["passes_scope_prescreen"]
    ].copy()
    scope_excluded_df = publication_included_df[
        ~publication_included_df["passes_scope_prescreen"]
    ].copy()
    export_pair("05", "scope_based_screening", scope_included_df, scope_excluded_df)

    scope_included_df["title_text_normalized"] = scope_included_df[
        "representative_title"
    ].apply(normalize_title)
    scope_included_df["has_semantic_title_signal"] = scope_included_df[
        "title_text_normalized"
    ].apply(lambda value: has_any_term(value, SEMANTIC_TITLE_TERMS))
    scope_included_df["has_domain_title_signal"] = scope_included_df[
        "title_text_normalized"
    ].apply(lambda value: has_any_term(value, DOMAIN_TITLE_TERMS))
    scope_included_df["has_model_title_signal"] = scope_included_df[
        "title_text_normalized"
    ].apply(lambda value: has_any_term(value, MODEL_TITLE_TERMS))
    scope_included_df["has_review_title_signal"] = scope_included_df[
        "title_text_normalized"
    ].apply(lambda value: has_any_term(value, REVIEW_TITLE_TERMS))
    scope_included_df["has_application_title_signal"] = scope_included_df[
        "title_text_normalized"
    ].apply(lambda value: has_any_term(value, APPLICATION_TITLE_TERMS))
    scope_included_df["passes_rule_based_title_screen"] = (
        (
            scope_included_df["has_semantic_title_signal"]
            & scope_included_df["has_domain_title_signal"]
        )
        | (
            scope_included_df["has_model_title_signal"]
            & scope_included_df["has_domain_title_signal"]
        )
        | (
            scope_included_df["has_review_title_signal"]
            & scope_included_df["has_domain_title_signal"]
        )
        | (
            scope_included_df["has_application_title_signal"]
            & scope_included_df["has_domain_title_signal"]
        )
    )
    title_included_df = scope_included_df[
        scope_included_df["passes_rule_based_title_screen"]
    ].copy()
    title_excluded_df = scope_included_df[
        ~scope_included_df["passes_rule_based_title_screen"]
    ].copy()
    export_pair("06", "rule_based_title_screening", title_included_df, title_excluded_df)

    screening_summary_df = pd.DataFrame(
        [
            {
                "screening_step": "Title presence filter",
                "included": len(usable_title_df),
                "excluded": len(blank_title_df),
            },
            {
                "screening_step": "Deduplication",
                "included": len(dedup_included_df),
                "excluded": len(dedup_excluded_df),
            },
            {
                "screening_step": "Language screening",
                "included": len(language_included_df),
                "excluded": len(language_excluded_df),
            },
            {
                "screening_step": "Publication-format screening",
                "included": len(publication_included_df),
                "excluded": len(publication_excluded_df),
            },
            {
                "screening_step": "Scope-based screening",
                "included": len(scope_included_df),
                "excluded": len(scope_excluded_df),
            },
            {
                "screening_step": "Rule-based title screening",
                "included": len(title_included_df),
                "excluded": len(title_excluded_df),
            },
        ]
    )
    screening_summary_df.to_excel(EXPORT_DIR / "screening_summary.xlsx", index=False)

    print("Lens-new-only pipeline completed.")
    print(f"Workspace: {BASE_DIR}")
    print()
    for row in screening_summary_df.itertuples(index=False):
        print(
            f"{row.screening_step}: included={row.included}, excluded={row.excluded}"
        )


if __name__ == "__main__":
    main()
