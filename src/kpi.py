"""Calculate dashboard KPIs and KPI summary tables from cleaned project data.

Run from the project root:
    python -m src.kpi
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "cleaned_data.csv"
OUTPUT_DIR = ROOT / "outputs" / "analysis"

REQUIRED_COLUMNS = {
    "Product_ID", "Category", "Competitor", "Price", "Discount_Percent",
    "Rating", "Review_Count", "Units_Sold", "Date", "Revenue"
}


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {DATA_PATH}\n"
            "Run the preprocessing module first: python -m src.preprocessing"
        )
    df = pd.read_csv(DATA_PATH)
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError("Required column(s) missing from cleaned dataset: " + ", ".join(missing))
    return df


def calculate_kpis(df: pd.DataFrame) -> pd.DataFrame:
    # These are observations across products, competitors and dates. Revenue and units sold
    # are synthetic in this project, not verified real-world sales figures.
    avg_price = df["Price"].mean()
    median_price = df["Price"].median()
    avg_discount = df["Discount_Percent"].mean()
    avg_rating = df["Rating"].mean()
    lowest_price_competitor = df.groupby("Competitor")["Price"].mean().idxmin()
    highest_price_category = df.groupby("Category")["Price"].mean().idxmax()
    highest_discount_competitor = df.groupby("Competitor")["Discount_Percent"].mean().idxmax()

    values = [
        ("Total dataset observations", int(len(df)), "Rows across product, competitor and date observations"),
        ("Unique products", int(df["Product_ID"].nunique()), "Distinct Product_ID values"),
        ("Number of categories", int(df["Category"].nunique()), "Distinct categories"),
        ("Number of competitors", int(df["Competitor"].nunique()), "Distinct competitors"),
        ("Average selling price (INR)", round(float(avg_price), 2), "Mean Price across all observations"),
        ("Median selling price (INR)", round(float(median_price), 2), "Median Price across all observations"),
        ("Average discount (%)", round(float(avg_discount), 2), "Mean Discount_Percent across all observations"),
        ("Average rating (out of 5)", round(float(avg_rating), 2), "Mean Rating across all observations"),
        ("Average review count", round(float(df["Review_Count"].mean()), 2), "Mean Review_Count across all observations"),
        ("Total simulated units sold across observations", int(df["Units_Sold"].sum()), "Synthetic Units_Sold summed across rows; not real-world sales"),
        ("Total simulated revenue across observations (INR)", round(float(df["Revenue"].sum()), 2), "Synthetic Revenue summed across rows; not real-world revenue"),
        ("Lowest average-price competitor", lowest_price_competitor, "Competitor with lowest mean Price"),
        ("Highest average-price category", highest_price_category, "Category with highest mean Price"),
        ("Highest average-discount competitor", highest_discount_competitor, "Competitor with highest mean Discount_Percent"),
    ]
    return pd.DataFrame(values, columns=["KPI", "Value", "Definition"])


def build_summary_tables(df: pd.DataFrame) -> None:
    category = df.groupby("Category", dropna=False).agg(
        Product_Observations=("Product_ID", "size"),
        Unique_Products=("Product_ID", "nunique"),
        Average_Price=("Price", "mean"),
        Median_Price=("Price", "median"),
        Minimum_Price=("Price", "min"),
        Maximum_Price=("Price", "max"),
        Price_Std_Dev=("Price", "std"),
        Average_Discount_Percent=("Discount_Percent", "mean"),
        Average_Rating=("Rating", "mean"),
        Total_Units_Sold=("Units_Sold", "sum"),
        Total_Simulated_Revenue=("Revenue", "sum"),
    ).reset_index().sort_values("Average_Price", ascending=False)

    competitor = df.groupby("Competitor", dropna=False).agg(
        Product_Observations=("Product_ID", "size"),
        Unique_Products=("Product_ID", "nunique"),
        Average_Price=("Price", "mean"),
        Median_Price=("Price", "median"),
        Average_Discount_Percent=("Discount_Percent", "mean"),
        Average_Rating=("Rating", "mean"),
        Average_Review_Count=("Review_Count", "mean"),
        Total_Units_Sold=("Units_Sold", "sum"),
        Total_Simulated_Revenue=("Revenue", "sum"),
    ).reset_index().sort_values("Average_Price", ascending=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    category.to_csv(OUTPUT_DIR / "category_kpis.csv", index=False)
    competitor.to_csv(OUTPUT_DIR / "competitor_kpis.csv", index=False)


def main() -> None:
    df = load_data()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    kpis = calculate_kpis(df)
    kpis.to_csv(OUTPUT_DIR / "kpi_summary.csv", index=False)
    build_summary_tables(df)
    print(f"Loaded {len(df):,} observations and {df['Product_ID'].nunique():,} unique products.")
    print("Saved KPI files:")
    print(f"  {OUTPUT_DIR / 'kpi_summary.csv'}")
    print(f"  {OUTPUT_DIR / 'category_kpis.csv'}")
    print(f"  {OUTPUT_DIR / 'competitor_kpis.csv'}")
    print("Note: units sold and revenue are simulated values in this dataset.")


if __name__ == "__main__":
    main()
