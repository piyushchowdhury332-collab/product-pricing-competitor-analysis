"""Clean and validate the synthetic product pricing dataset.

This script uses only regular Python modules and Pandas. It does not use a
notebook environment. The source data is synthetic and is intended for learning
and demonstration, not as evidence of actual market behaviour.
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from config import PROCESSED_DATA_DIR, RAW_DATA_FILE

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "Product_ID",
    "Product_Name",
    "Category",
    "Brand",
    "Competitor",
    "Price",
    "Original_Price",
    "Discount_Percent",
    "Rating",
    "Review_Count",
    "Features_Count",
    "Units_Sold",
    "Date",
]
NUMERIC_COLUMNS = [
    "Price",
    "Original_Price",
    "Discount_Percent",
    "Rating",
    "Review_Count",
    "Features_Count",
    "Units_Sold",
]
COUNT_COLUMNS = ["Review_Count", "Features_Count", "Units_Sold"]
KEY_COLUMNS = ["Product_ID", "Competitor", "Date"]


def load_raw_data(file_path: Path = RAW_DATA_FILE) -> pd.DataFrame:
    """Load the raw CSV after checking that it exists and has required fields."""
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Raw dataset not found: {file_path}. Run 'python -m src.data_generator' first."
        )

    dataframe = pd.read_csv(file_path)
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(dataframe.columns))
    if missing_columns:
        raise ValueError(f"Raw dataset is missing required columns: {missing_columns}")
    LOGGER.info("Loaded raw dataset with %s rows and %s columns", *dataframe.shape)
    return dataframe


def clean_data(raw_dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Clean records, validate business rules, and add analysis-ready metrics.

    No made-up values are inserted. Records with missing identifiers, invalid
    dates, invalid prices, invalid ratings, or invalid count metrics are removed.
    The discount percentage is recalculated from original and selling prices so
    the two price fields remain internally consistent.
    """
    dataframe = raw_dataframe.copy()
    audit: dict[str, int] = {"input_rows": int(len(dataframe))}
    audit["missing_cells_before_cleaning"] = int(dataframe.isna().sum().sum())

    # Normalize text fields without changing the meaning of their values.
    text_columns = ["Product_ID", "Product_Name", "Category", "Brand", "Competitor"]
    for column in text_columns:
        dataframe[column] = dataframe[column].astype("string").str.strip()
        dataframe[column] = dataframe[column].replace("", pd.NA)

    # Convert dates and numeric data explicitly, turning unparseable values into missing values.
    dataframe["Date"] = pd.to_datetime(dataframe["Date"], errors="coerce")
    for column in NUMERIC_COLUMNS:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    before = len(dataframe)
    dataframe = dataframe.dropna(subset=text_columns + ["Date"])
    audit["rows_removed_missing_identifiers_or_invalid_date"] = int(before - len(dataframe))

    before = len(dataframe)
    dataframe = dataframe.drop_duplicates(subset=KEY_COLUMNS, keep="first")
    audit["duplicate_business_keys_removed"] = int(before - len(dataframe))

    # Count-like columns must be present, finite, non-negative whole numbers.
    invalid_counts = pd.Series(False, index=dataframe.index)
    for column in COUNT_COLUMNS:
        values = dataframe[column]
        invalid_counts |= values.isna() | ~np.isfinite(values) | (values < 0) | (values % 1 != 0)
    before = len(dataframe)
    dataframe = dataframe.loc[~invalid_counts].copy()
    audit["rows_removed_invalid_count_metrics"] = int(before - len(dataframe))

    # Validate price and rating fields before feature engineering.
    invalid_price = (
        dataframe["Price"].isna()
        | dataframe["Original_Price"].isna()
        | ~np.isfinite(dataframe["Price"])
        | ~np.isfinite(dataframe["Original_Price"])
        | (dataframe["Price"] <= 0)
        | (dataframe["Original_Price"] <= 0)
        | (dataframe["Original_Price"] < dataframe["Price"])
    )
    invalid_rating = (
        dataframe["Rating"].isna()
        | ~np.isfinite(dataframe["Rating"])
        | (dataframe["Rating"] < 1)
        | (dataframe["Rating"] > 5)
    )
    before = len(dataframe)
    dataframe = dataframe.loc[~(invalid_price | invalid_rating)].copy()
    audit["rows_removed_invalid_price_or_rating"] = int(before - len(dataframe))

    # Remove rows where there is no usable category or competitor label (already
    # checked above); derive consistent discount metrics from the two price fields.
    dataframe["Discount_Amount"] = dataframe["Original_Price"] - dataframe["Price"]
    dataframe["Discount_Rate"] = (
        dataframe["Discount_Amount"] / dataframe["Original_Price"] * 100
    ).round(2)
    dataframe["Discount_Percent"] = dataframe["Discount_Rate"]

    # Extra metrics used later by the Streamlit app and Power BI model.
    category_average = dataframe.groupby("Category")["Price"].transform("mean")
    dataframe["Price_Index"] = (dataframe["Price"] / category_average).round(4)
    dataframe["Revenue"] = dataframe["Price"] * dataframe["Units_Sold"]

    # Consistent data types and presentation ordering.
    dataframe["Date"] = dataframe["Date"].dt.strftime("%Y-%m-%d")
    for column in COUNT_COLUMNS:
        dataframe[column] = dataframe[column].astype("int64")
    dataframe["Price"] = dataframe["Price"].round().astype("int64")
    dataframe["Original_Price"] = dataframe["Original_Price"].round().astype("int64")
    dataframe["Rating"] = dataframe["Rating"].round(2)
    dataframe["Discount_Percent"] = dataframe["Discount_Percent"].round(2)
    dataframe["Discount_Amount"] = dataframe["Discount_Amount"].round().astype("int64")
    dataframe["Price_Index"] = dataframe["Price_Index"].round(4)
    dataframe["Revenue"] = dataframe["Revenue"].round().astype("int64")

    dataframe = dataframe.sort_values(KEY_COLUMNS).reset_index(drop=True)
    audit["output_rows"] = int(len(dataframe))
    audit["rows_removed_total"] = int(audit["input_rows"] - audit["output_rows"])
    audit["missing_cells_after_cleaning"] = int(dataframe.isna().sum().sum())
    return dataframe, audit


def save_outputs(cleaned_dataframe: pd.DataFrame, audit: dict[str, int]) -> tuple[Path, Path]:
    """Save the cleaned CSV and a concise text audit report."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = PROCESSED_DATA_DIR / "cleaned_data.csv"
    report_path = PROCESSED_DATA_DIR / "cleaning_report.txt"
    cleaned_dataframe.to_csv(csv_path, index=False, encoding="utf-8")

    with report_path.open("w", encoding="utf-8") as report:
        report.write("PRODUCT PRICING DATA CLEANING REPORT\n")
        report.write("Dataset type: Synthetic demonstration data\n\n")
        for label, value in audit.items():
            report.write(f"{label}: {value}\n")
        report.write("\nFINAL DATASET SUMMARY\n")
        report.write(f"Rows: {len(cleaned_dataframe)}\n")
        report.write(f"Columns: {len(cleaned_dataframe.columns)}\n")
        report.write(f"Categories: {cleaned_dataframe['Category'].nunique()}\n")
        report.write(f"Competitors: {cleaned_dataframe['Competitor'].nunique()}\n")
        report.write(f"Unique products: {cleaned_dataframe['Product_ID'].nunique()}\n")
        report.write(f"Observation dates: {cleaned_dataframe['Date'].nunique()}\n")
        report.write(f"Minimum selling price: INR {cleaned_dataframe['Price'].min():,.0f}\n")
        report.write(f"Maximum selling price: INR {cleaned_dataframe['Price'].max():,.0f}\n")
        report.write("\nNote: all records and values are simulated and are not actual market data.\n")

    return csv_path, report_path


def main() -> None:
    """Run the end-to-end cleaning pipeline and print its audit summary."""
    raw_dataframe = load_raw_data()
    cleaned_dataframe, audit = clean_data(raw_dataframe)
    csv_path, report_path = save_outputs(cleaned_dataframe, audit)
    LOGGER.info("Cleaning complete. Saved %s rows and %s columns to %s", *cleaned_dataframe.shape, csv_path)
    LOGGER.info("Rows removed during cleaning: %s", audit["rows_removed_total"])
    LOGGER.info("Missing cells after cleaning: %s", audit["missing_cells_after_cleaning"])
    LOGGER.info("Cleaning report saved to %s", report_path)


if __name__ == "__main__":
    main()
