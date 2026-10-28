"""
Product Pricing & Competitor Analysis: visualization module.
Run from the project root with:
    python -m src.visualization

Creates readable PNG charts in outputs/visualizations.
All charts use the project's processed CSV and analysis summaries.
The dataset is synthetic; revenue and units sold are simulated.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "cleaned_data.csv"
ANALYSIS = ROOT / "outputs" / "analysis"
OUT = ROOT / "outputs" / "visualizations"

def save_chart(fig, filename, note=None):
    if note:
        fig.text(0.01, 0.01, note, fontsize=8, wrap=True)
        fig.tight_layout(rect=(0, 0.06, 1, 1))
    else:
        fig.tight_layout()
    fig.savefig(OUT / filename, dpi=220, bbox_inches="tight")
    plt.close(fig)

def load_inputs():
    required = [DATA, ANALYSIS / "category_summary.csv",
                ANALYSIS / "competitor_summary.csv",
                ANALYSIS / "monthly_summary.csv",
                ANALYSIS / "category_competitor_summary.csv",
                ANALYSIS / "product_summary.csv",
                ANALYSIS / "correlation_matrix.csv"]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required project file(s): " + ", ".join(missing))
    df = pd.read_csv(DATA)
    cat = pd.read_csv(ANALYSIS / "category_summary.csv")
    comp = pd.read_csv(ANALYSIS / "competitor_summary.csv")
    monthly = pd.read_csv(ANALYSIS / "monthly_summary.csv").sort_values("Month")
    cat_comp = pd.read_csv(ANALYSIS / "category_competitor_summary.csv")
    prod = pd.read_csv(ANALYSIS / "product_summary.csv")
    corr = pd.read_csv(ANALYSIS / "correlation_matrix.csv").set_index("Metric")
    return df, cat, comp, monthly, cat_comp, prod, corr

def chart_average_price_by_category(cat):
    d = cat.sort_values("Average_Price")
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(d["Category"], d["Average_Price"])
    ax.set(title="Average Selling Price by Category", xlabel="Average selling price (₹)")
    ax.grid(axis="x", alpha=.25)
    ax.bar_label(bars, labels=[f"₹{v:,.0f}" for v in d["Average_Price"]], padding=4, fontsize=8)
    save_chart(fig, "01_average_price_by_category.png")

def chart_average_price_by_competitor(comp):
    d = comp.sort_values("Average_Price")
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(d["Competitor"], d["Average_Price"])
    ax.set(title="Average Selling Price by Competitor", xlabel="Average selling price (₹)")
    ax.grid(axis="x", alpha=.25)
    ax.bar_label(bars, labels=[f"₹{v:,.0f}" for v in d["Average_Price"]], padding=4, fontsize=9)
    save_chart(fig, "02_average_price_by_competitor.png")

def chart_monthly_trends(monthly):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly["Month"], monthly["Average_Price"], marker="o", linewidth=2)
    ax.set(title="Monthly Average Selling Price", xlabel="Month", ylabel="Average selling price (₹)")
    ax.tick_params(axis="x", labelrotation=30)
    ax.grid(alpha=.25)
    for x, y in zip(monthly["Month"], monthly["Average_Price"]):
        ax.annotate(f"₹{y:,.0f}", (x, y), xytext=(0, 7), textcoords="offset points", ha="center", fontsize=8)
    save_chart(fig, "03_monthly_average_price.png")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly["Month"], monthly["Average_Discount_Percent"], marker="s", linewidth=2)
    ax.set(title="Monthly Average Discount", xlabel="Month", ylabel="Average discount (%)")
    ax.tick_params(axis="x", labelrotation=30)
    ax.grid(alpha=.25)
    for x, y in zip(monthly["Month"], monthly["Average_Discount_Percent"]):
        ax.annotate(f"{y:.1f}%", (x, y), xytext=(0, 7), textcoords="offset points", ha="center", fontsize=8)
    save_chart(fig, "04_monthly_average_discount.png")

def chart_monthly_revenue(monthly):
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(monthly["Month"], monthly["Total_Revenue"])
    ax.set(title="Simulated Revenue by Month", xlabel="Month", ylabel="Simulated revenue (₹)")
    ax.tick_params(axis="x", labelrotation=30)
    ax.grid(axis="y", alpha=.25)
    ax.bar_label(bars, labels=[f"₹{v:,.0f}" for v in monthly["Total_Revenue"]], padding=3, fontsize=8)
    save_chart(fig, "05_monthly_revenue.png", "Revenue is simulated and depends on the dataset's revenue calculation.")

def chart_category_competitor_heatmap(cat_comp):
    pivot = cat_comp.pivot(index="Category", columns="Competitor", values="Average_Price")
    fig, ax = plt.subplots(figsize=(11, 6.5))
    im = ax.imshow(pivot.values, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), labels=pivot.columns, rotation=25, ha="right")
    ax.set_yticks(range(len(pivot.index)), labels=pivot.index)
    ax.set_title("Average Selling Price by Category and Competitor")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"₹{pivot.iloc[i,j]:,.0f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="Average selling price (₹)")
    save_chart(fig, "06_category_competitor_price_heatmap.png")

def chart_price_vs_discount(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    for category, group in df.groupby("Category"):
        ax.scatter(group["Discount_Percent"], group["Price"], s=13, alpha=.28, label=category)
    ax.set(title="Selling Price vs Discount by Category", xlabel="Discount (%)", ylabel="Selling price (₹)")
    ax.legend(fontsize=8, ncol=2, frameon=False)
    ax.grid(alpha=.2)
    save_chart(fig, "07_price_vs_discount_scatter.png",
               "Each point is one product–competitor–month observation. Correlation does not establish causation.")

def chart_rating_vs_units_sold(df):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(df["Rating"], df["Units_Sold"], alpha=.28, s=15)
    ax.set(title="Product Rating vs Units Sold", xlabel="Rating (out of 5)", ylabel="Units sold (simulated)")
    ax.grid(alpha=.2)
    save_chart(fig, "08_rating_vs_units_sold.png",
               "Units sold are simulated; this chart shows association, not proof that ratings cause sales.")

def chart_correlation_matrix(corr):
    fig, ax = plt.subplots(figsize=(11, 8))
    im = ax.imshow(corr.values, aspect="auto", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)), corr.columns, rotation=40, ha="right")
    ax.set_yticks(range(len(corr.index)), corr.index)
    ax.set_title("Correlation Matrix of Numeric Metrics")
    for i in range(len(corr.index)):
        for j in range(len(corr.columns)):
            ax.text(j, i, f"{corr.iloc[i,j]:.2f}", ha="center", va="center", fontsize=7)
    fig.colorbar(im, ax=ax, label="Pearson correlation (−1 to +1)")
    save_chart(fig, "09_correlation_matrix.png")

def chart_top_products(prod):
    d = prod.nlargest(10, "Total_Revenue").sort_values("Total_Revenue")
    fig, ax = plt.subplots(figsize=(11, 7))
    bars = ax.barh(d["Product_Name"], d["Total_Revenue"])
    ax.set(title="Top 10 Products by Simulated Revenue", xlabel="Simulated revenue (₹)")
    ax.grid(axis="x", alpha=.25)
    ax.bar_label(bars, labels=[f"₹{v:,.0f}" for v in d["Total_Revenue"]], padding=4, fontsize=8)
    save_chart(fig, "10_top_10_products_by_revenue.png",
               "Revenue is simulated; rankings reflect this dataset, not actual market performance.")

def chart_revenue_by_category(cat):
    d = cat.sort_values("Total_Revenue")
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(d["Category"], d["Total_Revenue"])
    ax.set(title="Simulated Revenue by Category", xlabel="Simulated revenue (₹)")
    ax.grid(axis="x", alpha=.25)
    ax.bar_label(bars, labels=[f"₹{v:,.0f}" for v in d["Total_Revenue"]], padding=4, fontsize=8)
    save_chart(fig, "11_revenue_by_category.png",
               "Revenue is simulated; interpret as an example analysis only.")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"axes.titlesize": 15, "axes.labelsize": 11})
    df, cat, comp, monthly, cat_comp, prod, corr = load_inputs()
    chart_average_price_by_category(cat)
    chart_average_price_by_competitor(comp)
    chart_monthly_trends(monthly)
    chart_monthly_revenue(monthly)
    chart_category_competitor_heatmap(cat_comp)
    chart_price_vs_discount(df)
    chart_rating_vs_units_sold(df)
    chart_correlation_matrix(corr)
    chart_top_products(prod)
    chart_revenue_by_category(cat)
    print(f"Generated 11 charts in: {OUT}")

if __name__ == "__main__":
    main()
