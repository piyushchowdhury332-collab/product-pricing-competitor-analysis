# Product Pricing & Competitor Analysis

## Current project snapshot

This ZIP contains the Python data pipeline, cleaned dataset, descriptive analysis, KPI tables, and generated visualizations for the current project stage.

**Important:** This is a synthetic demonstration dataset, not real market data. Product, competitor, price, discount, rating, review, units-sold, and revenue values are simulated. Do not present the results as real-world market findings. Correlation does not prove causation, and the simulated sales values cannot establish real-world price elasticity.

## Included

- `data/raw/synthetic_products.csv`: synthetic input data (2,880 observations and 120 unique products)
- `data/processed/cleaned_data.csv`: cleaned data used by the analysis modules
- `data/processed/cleaning_report.txt`: cleaning report
- `src/`: modular Python scripts for generation, preprocessing, analysis, KPIs, and charts
- `outputs/analysis/`: analysis summaries, KPI tables, and automatically calculated findings
- `outputs/visualizations/`: 18 PNG charts plus a chart guide
- `config.py`: dataset generation settings

## Setup on Windows PowerShell

Open a terminal in this project folder and run:

```powershell
python -m pip install -r requirements.txt
```

## Re-run the complete data and analysis pipeline

Run these commands from the project root, in this order:

```powershell
python -m src.data_generator
python -m src.preprocessing
python -m src.analysis
python -m src.visualization
python -m src.kpi
python -m src.required_visualizations
```

The generator recreates the synthetic raw CSV with the configured random seed. The later modules recreate their outputs. The charts are saved in `outputs/visualizations/` and summary tables are saved in `outputs/analysis/`.

## Current status / pending work

Included in this snapshot: dataset generation, cleaning, summary analysis, KPI calculation, and 18 static visualizations.

Not included yet: an interactive Streamlit dashboard, Power BI report, final testing evidence, and final project report/demo materials. These should be completed before describing the entire project as finished.

## Streamlit dashboard

From the project root:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The dashboard reads `data/processed/cleaned_data.csv`, supports category, competitor, brand and date filters, and shows interactive summaries, comparisons, trends, and product-level exploration. Static charts are also viewable. All data is synthetic and sales/revenue are simulated.
# product-pricing-competitor-analysis
