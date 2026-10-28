"""Create reproducible pricing analysis summaries from the cleaned CSV.

All input records in this student project are synthetic demonstration data.
This module reports descriptive patterns; it does not claim causal effects.
Run from the project root with: python -m src.analysis
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "cleaned_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "analysis"

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

REQUIRED_COLUMNS = {
    "Product_ID", "Product_Name", "Category", "Brand", "Competitor",
    "Price", "Original_Price", "Discount_Percent", "Rating",
    "Review_Count", "Features_Count", "Units_Sold", "Date",
}
NUMERIC_COLUMNS = [
    "Price", "Original_Price", "Discount_Percent", "Rating",
    "Review_Count", "Features_Count", "Units_Sold",
]


def load_cleaned_data(file_path: Path = INPUT_FILE) -> pd.DataFrame:
    """Load the cleaned dataset and validate required columns."""
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {file_path}. Run 'python -m src.preprocessing' first."
        )
    dataframe = pd.read_csv(file_path)
    missing = sorted(REQUIRED_COLUMNS - set(dataframe.columns))
    if missing:
        raise ValueError(f"Cleaned dataset is missing required columns: {missing}")
    for column in NUMERIC_COLUMNS:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")
    dataframe["Date"] = pd.to_datetime(dataframe["Date"], errors="coerce")
    if dataframe.empty:
        raise ValueError("The cleaned dataset contains no records.")
    if dataframe["Price"].isna().any() or (dataframe["Price"] <= 0).any():
        raise ValueError("Price contains missing or non-positive values. Rerun data cleaning.")
    return dataframe


def build_summaries(dataframe: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Calculate descriptive pricing, competitor, product and correlation summaries."""
    data = dataframe.copy()
    if "Discount_Amount" not in data:
        data["Discount_Amount"] = data["Original_Price"] - data["Price"]
    if "Revenue" not in data:
        data["Revenue"] = data["Price"] * data["Units_Sold"]
    if "Price_Index" not in data:
        category_average = data.groupby("Category")["Price"].transform("mean")
        data["Price_Index"] = data["Price"] / category_average

    category_summary = data.groupby("Category", dropna=False).agg(
        Product_Observations=("Product_ID", "count"),
        Unique_Products=("Product_ID", "nunique"),
        Average_Price=("Price", "mean"),
        Median_Price=("Price", "median"),
        Minimum_Price=("Price", "min"),
        Maximum_Price=("Price", "max"),
        Price_Std_Dev=("Price", "std"),
        Average_Discount_Percent=("Discount_Percent", "mean"),
        Average_Rating=("Rating", "mean"),
        Total_Units_Sold=("Units_Sold", "sum"),
        Total_Revenue=("Revenue", "sum"),
    ).reset_index().sort_values("Average_Price", ascending=False)

    competitor_summary = data.groupby("Competitor", dropna=False).agg(
        Product_Observations=("Product_ID", "count"),
        Unique_Products=("Product_ID", "nunique"),
        Average_Price=("Price", "mean"),
        Median_Price=("Price", "median"),
        Average_Discount_Percent=("Discount_Percent", "mean"),
        Average_Rating=("Rating", "mean"),
        Average_Review_Count=("Review_Count", "mean"),
        Total_Units_Sold=("Units_Sold", "sum"),
        Total_Revenue=("Revenue", "sum"),
    ).reset_index().sort_values("Average_Price")

    category_competitor = data.groupby(["Category", "Competitor"], dropna=False).agg(
        Observations=("Product_ID", "count"),
        Average_Price=("Price", "mean"),
        Median_Price=("Price", "median"),
        Average_Discount_Percent=("Discount_Percent", "mean"),
        Average_Rating=("Rating", "mean"),
        Total_Revenue=("Revenue", "sum"),
    ).reset_index().sort_values(["Category", "Average_Price"])

    product_summary = data.groupby(
        ["Product_ID", "Product_Name", "Category", "Brand"], dropna=False
    ).agg(
        Observation_Count=("Price", "count"),
        Average_Price=("Price", "mean"),
        Minimum_Price=("Price", "min"),
        Maximum_Price=("Price", "max"),
        Average_Discount_Percent=("Discount_Percent", "mean"),
        Average_Rating=("Rating", "mean"),
        Average_Review_Count=("Review_Count", "mean"),
        Total_Units_Sold=("Units_Sold", "sum"),
        Total_Revenue=("Revenue", "sum"),
        Average_Price_Index=("Price_Index", "mean"),
    ).reset_index()
    product_summary["Average_Price"] = product_summary["Average_Price"].round(2)
    product_summary["Category_Price_Position"] = np.select(
        [product_summary["Average_Price_Index"] > 1.10,
         product_summary["Average_Price_Index"] < 0.90],
        ["Above category average", "Below category average"],
        default="Near category average",
    )
    product_summary = product_summary.sort_values("Average_Price", ascending=False)

    numeric_for_corr = [
        "Price", "Original_Price", "Discount_Percent", "Rating",
        "Review_Count", "Features_Count", "Units_Sold", "Revenue",
    ]
    correlation = data[numeric_for_corr].corr(numeric_only=True).reset_index(names="Metric")

    monthly_summary = data.groupby(data["Date"].dt.to_period("M")).agg(
        Average_Price=("Price", "mean"),
        Average_Discount_Percent=("Discount_Percent", "mean"),
        Total_Units_Sold=("Units_Sold", "sum"),
        Total_Revenue=("Revenue", "sum"),
    ).reset_index(names="Month")
    monthly_summary["Month"] = monthly_summary["Month"].astype(str)

    return {
        "category_summary": category_summary,
        "competitor_summary": competitor_summary,
        "category_competitor_summary": category_competitor,
        "product_summary": product_summary,
        "correlation_matrix": correlation,
        "monthly_summary": monthly_summary,
    }


def save_summaries(summaries: dict[str, pd.DataFrame], output_dir: Path = OUTPUT_DIR) -> list[Path]:
    """Write all summary tables to CSV files and return the created paths."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    created_files: list[Path] = []
    for name, summary in summaries.items():
        output_path = output_dir / f"{name}.csv"
        summary.to_csv(output_path, index=False, encoding="utf-8")
        created_files.append(output_path)
    return created_files


def write_findings(dataframe: pd.DataFrame, summaries: dict[str, pd.DataFrame], output_dir: Path = OUTPUT_DIR) -> Path:
    """Write a concise, automatically calculated business findings report."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    category = summaries["category_summary"]
    competitor = summaries["competitor_summary"]
    data = dataframe.copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    average_price = data["Price"].mean()
    median_price = data["Price"].median()
    highest_category = category.iloc[0]
    lowest_competitor = competitor.iloc[0]
    highest_discount_competitor = competitor.loc[competitor["Average_Discount_Percent"].idxmax()]
    most_revenue_category = category.loc[category["Total_Revenue"].idxmax()]
    price_rating_corr = data[["Price", "Rating"]].corr().iloc[0, 1]
    price_reviews_corr = data[["Price", "Review_Count"]].corr().iloc[0, 1]

    report_path = output_dir / "business_findings.txt"
    with report_path.open("w", encoding="utf-8") as report:
        report.write("PRODUCT PRICING & COMPETITOR ANALYSIS: FINDINGS\n")
        report.write("Dataset type: synthetic demonstration data\n")
        report.write("These findings describe the generated dataset only. They are not actual market evidence and do not prove causation.\n\n")
        report.write(f"Observation rows: {len(data):,}\n")
        report.write(f"Unique products: {data['Product_ID'].nunique():,}\n")
        report.write(f"Categories: {data['Category'].nunique():,}\n")
        report.write(f"Competitors: {data['Competitor'].nunique():,}\n")
        report.write(f"Observation dates: {data['Date'].nunique():,}\n")
        report.write(f"Overall average selling price: INR {average_price:,.2f}\n")
        report.write(f"Overall median selling price: INR {median_price:,.2f}\n\n")
        report.write(f"Highest average-price category: {highest_category['Category']} (INR {highest_category['Average_Price']:,.2f})\n")
        report.write(f"Lowest average-price competitor: {lowest_competitor['Competitor']} (INR {lowest_competitor['Average_Price']:,.2f})\n")
        report.write(f"Highest average-discount competitor: {highest_discount_competitor['Competitor']} ({highest_discount_competitor['Average_Discount_Percent']:.2f}%)\n")
        report.write(f"Highest-revenue category in simulated data: {most_revenue_category['Category']} (INR {most_revenue_category['Total_Revenue']:,.2f})\n")
        report.write(f"Price-rating Pearson correlation: {price_rating_corr:.3f}\n")
        report.write(f"Price-review-count Pearson correlation: {price_reviews_corr:.3f}\n\n")
        report.write("Interpretation notes:\n")
        report.write("- Correlation describes association, not causation.\n")
        report.write("- Competitor averages are descriptive; matched product comparisons should be used for stronger fairness.\n")
        report.write("- Simulated units sold cannot establish real-world price elasticity.\n")
    return report_path


def main() -> None:
    """Run analysis and export summary CSVs plus a findings report."""
    dataframe = load_cleaned_data()
    summaries = build_summaries(dataframe)
    created_files = save_summaries(summaries)
    findings_path = write_findings(dataframe, summaries)
    LOGGER.info("Analysis completed for %s rows.", f"{len(dataframe):,}")
    for path in created_files:
        LOGGER.info("Saved summary: %s", path)
    LOGGER.info("Saved business findings: %s", findings_path)


if __name__ == "__main__":
    main()
