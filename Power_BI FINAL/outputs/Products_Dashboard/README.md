# Product Performance Dashboard

Open `Products.pbip` in Power BI Desktop. The report imports the included `cleaned_data.csv`; the model query points to this copy of the CSV.

## Pages

- **Executive Overview** — headline revenue, units, distinct products, and average rating; monthly revenue; category and brand revenue; competitor discount rate.
- **Category & Brand** — revenue, units, and distinct product comparisons by category and brand.
- **Pricing & Customer** — average price and rating, discount rate by competitor, and review volume by brand.

Each page has interactive month and category selectors, with brand or competitor selection where relevant. Visual selections cross-filter other visuals on that page.

## Data coverage

The provided source has 2,880 product-month records, covering 120 distinct products and six monthly dates from April 1 through September 1, 2026. Revenue and units sum across those records. The source contains no prior-year period, so the dashboard does not present year-over-year comparisons. Currency is not specified in the source, so monetary measures are shown without a currency symbol.
