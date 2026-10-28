# Visualizations

This folder contains **18 generated charts** for the Product Pricing & Competitor Analysis project. The charts are based on synthetic data only and are not real market observations.

## Chart list

1. Average price by category
2. Average price by competitor
3. Monthly average price
4. Monthly average discount
5. Monthly simulated revenue
6. Category-competitor price heatmap
7. Price vs. discount scatter plot
8. Rating vs. simulated units sold
9. Correlation matrix
10. Top 10 products by simulated revenue
11. Simulated revenue by category
12. Price distribution histogram
13. Price box plot by category
14. Price box plot by competitor
15. Price vs. rating
16. Price vs. review count
17. Average discount by competitor
18. Monthly simulated units sold

## Run

From the project root, install dependencies with `python -m pip install -r requirements.txt`, then run:

```powershell
python -m src.visualization
python -m src.required_visualizations
```

The first command regenerates the original set of charts; the second generates the additional charts. Both save PNGs in `outputs/visualizations/`.

Interpretation cautions: correlation describes association, not causation. All sales and revenue fields are simulated and must be labelled accordingly.
