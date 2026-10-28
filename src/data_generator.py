"""Generate reproducible synthetic product pricing records for project development."""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from config import (
    CATEGORY_PRICE_RANGES,
    CATEGORY_PRODUCT_TYPES,
    COMPETITORS,
    NUMBER_OF_PRODUCTS,
    OBSERVATION_MONTHS,
    RANDOM_SEED,
    RAW_DATA_DIR,
    RAW_DATA_FILE,
    SYNTHETIC_BRANDS,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger(__name__)


def _build_product_catalog(rng: np.random.Generator, count: int) -> list[dict]:
    """Create a catalog of unique simulated products."""
    categories = list(CATEGORY_PRICE_RANGES)
    catalog: list[dict] = []

    for product_number in range(1, count + 1):
        category = categories[(product_number - 1) % len(categories)]
        low_price, high_price = CATEGORY_PRICE_RANGES[category]
        base_price = float(np.exp(rng.uniform(np.log(low_price), np.log(high_price))))
        product_type = str(rng.choice(CATEGORY_PRODUCT_TYPES[category]))
        brand = str(rng.choice(SYNTHETIC_BRANDS))
        model_number = 100 + product_number
        base_rating = float(np.clip(rng.normal(4.1, 0.35), 2.8, 4.9))
        base_review_count = int(rng.integers(25, 12000))
        features_count = int(rng.integers(3, 16))

        catalog.append({
            "Product_ID": f"P{product_number:04d}",
            "Product_Name": f"{brand} {product_type} Model {model_number}",
            "Category": category,
            "Brand": brand,
            "Base_Price": base_price,
            "Base_Rating": base_rating,
            "Base_Review_Count": base_review_count,
            "Features_Count": features_count,
        })

    return catalog


def generate_dataset(output_path: Path = RAW_DATA_FILE) -> pd.DataFrame:
    """Generate synthetic competitor and monthly pricing observations and save a CSV.

    Each product is listed by each configured competitor in each configured month.
    The values are simulated for demonstrating a data analytics workflow and are not
    actual market, customer, or sales data.
    """
    if NUMBER_OF_PRODUCTS < 1:
        raise ValueError("NUMBER_OF_PRODUCTS must be at least 1.")
    if not COMPETITORS or not OBSERVATION_MONTHS:
        raise ValueError("Configure at least one competitor and one observation month.")

    rng = np.random.default_rng(RANDOM_SEED)
    catalog = _build_product_catalog(rng, NUMBER_OF_PRODUCTS)
    rows: list[dict] = []

    # Retailer pricing multipliers are configured here as simulation assumptions.
    competitor_price_factors = {
        competitor: float(factor)
        for competitor, factor in zip(COMPETITORS, np.linspace(0.92, 1.08, len(COMPETITORS)))
    }
    competitor_demand_factors = {
        competitor: float(factor)
        for competitor, factor in zip(COMPETITORS, np.linspace(1.12, 0.88, len(COMPETITORS)))
    }

    for product in catalog:
        for month_index, month in enumerate(OBSERVATION_MONTHS):
            seasonal_factor = 1.0 + 0.025 * np.sin(month_index * np.pi / 3)
            for competitor in COMPETITORS:
                listed_price = product["Base_Price"] * competitor_price_factors[competitor] * seasonal_factor
                discount_rate = float(rng.uniform(0.05, 0.36))
                selling_price = max(1, round(listed_price * (1 - discount_rate)))
                original_price = max(selling_price, round(listed_price))
                discount_percent = round((original_price - selling_price) / original_price * 100, 2)

                rating = float(np.clip(product["Base_Rating"] + rng.normal(0, 0.12), 1.0, 5.0))
                month_review_growth = 1 + month_index * float(rng.uniform(0.005, 0.025))
                review_count = max(1, int(product["Base_Review_Count"] * month_review_growth * rng.uniform(0.85, 1.15)))

                # Synthetic sales are simulated for practicing analysis only.
                relative_price_factor = product["Base_Price"] / max(selling_price, 1)
                promotion_factor = 1 + discount_percent / 100 * 0.7
                rating_factor = max(0.5, rating / 4.0)
                monthly_baseline = max(5, 1800 / np.sqrt(max(product["Base_Price"], 1)))
                units_sold = int(max(0, rng.normal(
                    monthly_baseline
                    * competitor_demand_factors[competitor]
                    * relative_price_factor
                    * promotion_factor
                    * rating_factor,
                    max(2, monthly_baseline * 0.25),
                )))

                rows.append({
                    "Product_ID": product["Product_ID"],
                    "Product_Name": product["Product_Name"],
                    "Category": product["Category"],
                    "Brand": product["Brand"],
                    "Competitor": competitor,
                    "Price": selling_price,
                    "Original_Price": original_price,
                    "Discount_Percent": discount_percent,
                    "Rating": round(rating, 2),
                    "Review_Count": review_count,
                    "Features_Count": product["Features_Count"],
                    "Units_Sold": units_sold,
                    "Date": month,
                })

    dataframe = pd.DataFrame(rows)
    expected_rows = len(catalog) * len(COMPETITORS) * len(OBSERVATION_MONTHS)
    if len(dataframe) != expected_rows:
        raise RuntimeError(f"Expected {expected_rows} records but generated {len(dataframe)}.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False, encoding="utf-8")
    LOGGER.info("Generated %s records and saved them to %s", f"{len(dataframe):,}", output_path)
    return dataframe


def main() -> None:
    """Run the synthetic data generation workflow and show a concise validation summary."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    dataframe = generate_dataset(RAW_DATA_FILE)
    LOGGER.info("Dataset shape: %s rows x %s columns", *dataframe.shape)
    LOGGER.info("Missing values: %s", int(dataframe.isna().sum().sum()))
    LOGGER.info("Unique products: %s", dataframe["Product_ID"].nunique())
    LOGGER.info("Competitors: %s", dataframe["Competitor"].nunique())
    LOGGER.info("Observation dates: %s", dataframe["Date"].nunique())
    LOGGER.info("Categories: %s", dataframe["Category"].nunique())
    LOGGER.info("Price range: ₹%s to ₹%s", f"{dataframe['Price'].min():,.0f}", f"{dataframe['Price'].max():,.0f}")


if __name__ == "__main__":
    main()
