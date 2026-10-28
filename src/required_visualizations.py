"""Generate additional visualizations listed in the project assignment.

Run from the project root:
    python -m src.required_visualizations
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "cleaned_data.csv"
OUT_DIR = ROOT / "outputs" / "visualizations"


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    required = {"Price", "Category", "Competitor", "Rating", "Review_Count", "Discount_Percent", "Date", "Units_Sold"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError("Required column(s) missing from cleaned dataset: " + ", ".join(missing))
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


def save(fig, filename: str, note: str | None = None) -> None:
    if note:
        fig.text(0.01, 0.01, note, fontsize=8, wrap=True)
        fig.tight_layout(rect=(0, 0.055, 1, 1))
    else:
        fig.tight_layout()
    fig.savefig(OUT_DIR / filename, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    df = load_data()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"axes.titlesize": 14, "axes.labelsize": 11})

    # 12. Price distribution histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df["Price"].dropna(), bins=30, edgecolor="black", alpha=0.8)
    ax.set(title="Overall Product Price Distribution", xlabel="Selling price (₹)", ylabel="Number of observations")
    ax.grid(axis="y", alpha=0.2)
    save(fig, "12_price_distribution_histogram.png")

    # 13. Price boxplot by category
    cats = sorted(df["Category"].dropna().unique())
    values = [df.loc[df["Category"] == c, "Price"].dropna().values for c in cats]
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.boxplot(values, tick_labels=cats, showfliers=False)
    ax.set(title="Price Distribution by Category", xlabel="Category", ylabel="Selling price (₹)")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.2)
    save(fig, "13_price_boxplot_by_category.png", "Outlier points are hidden for readability; the box still shows median and quartiles.")

    # 14. Price boxplot by competitor
    competitors = sorted(df["Competitor"].dropna().unique())
    values = [df.loc[df["Competitor"] == c, "Price"].dropna().values for c in competitors]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.boxplot(values, tick_labels=competitors, showfliers=False)
    ax.set(title="Price Distribution by Competitor", xlabel="Competitor", ylabel="Selling price (₹)")
    ax.grid(axis="y", alpha=0.2)
    save(fig, "14_price_boxplot_by_competitor.png", "Outlier points are hidden for readability; compare medians and spread.")

    # 15. Price vs rating scatter
    fig, ax = plt.subplots(figsize=(10, 6))
    for category, group in df.groupby("Category"):
        ax.scatter(group["Price"], group["Rating"], s=16, alpha=0.35, label=category)
    ax.set(title="Selling Price vs Customer Rating", xlabel="Selling price (₹)", ylabel="Rating (out of 5)")
    ax.legend(fontsize=8, ncol=2, frameon=False)
    ax.grid(alpha=0.2)
    save(fig, "15_price_vs_rating.png", "This chart shows association, not proof that price causes higher or lower ratings.")

    # 16. Price vs review count. Log scale helps when review counts span a wide range.
    positive = df[df["Review_Count"] > 0]
    fig, ax = plt.subplots(figsize=(10, 6))
    for competitor, group in positive.groupby("Competitor"):
        ax.scatter(group["Price"], group["Review_Count"], s=16, alpha=0.35, label=competitor)
    ax.set(title="Selling Price vs Review Count", xlabel="Selling price (₹)", ylabel="Review count (log scale)")
    ax.set_yscale("log")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(alpha=0.2, which="both")
    save(fig, "16_price_vs_review_count.png", "Review count is a descriptive popularity indicator, not a direct sales measure.")

    # 17. Average discount by competitor
    d = df.groupby("Competitor")["Discount_Percent"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(d.index, d.values)
    ax.set(title="Average Discount by Competitor", xlabel="Average discount (%)", ylabel="Competitor")
    ax.grid(axis="x", alpha=0.2)
    ax.bar_label(bars, labels=[f"{v:.1f}%" for v in d.values], padding=4, fontsize=9)
    save(fig, "17_average_discount_by_competitor.png")

    # 18. Monthly units sold as separate chart, because units and rupees should not share one axis.
    monthly = df.dropna(subset=["Date"]).assign(Month=lambda x: x["Date"].dt.to_period("M").astype(str))
    monthly = monthly.groupby("Month", as_index=False)["Units_Sold"].sum().sort_values("Month")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly["Month"], monthly["Units_Sold"], marker="o", linewidth=2)
    ax.set(title="Monthly Simulated Units Sold", xlabel="Month", ylabel="Units sold summed across observations")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(alpha=0.2)
    save(fig, "18_monthly_units_sold.png", "Units sold are simulated and summed across product–competitor–date observations.")

    print(f"Generated 7 additional charts in: {OUT_DIR}")
    print("Note: the dataset is synthetic; sales metrics are simulated.")


if __name__ == "__main__":
    main()
