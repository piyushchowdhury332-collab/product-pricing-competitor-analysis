"""Interactive dashboard for the synthetic Product Pricing & Competitor Analysis project."""
from pathlib import Path 
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'processed' / 'cleaned_data.csv'
CHARTS = ROOT / 'outputs' / 'visualizations'

from portal_auth import require_login
require_login()
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {--ink:#eaf0ff;--muted:#91a0ba;--line:#253351;--accent:#7c9dff;}
html, body, [class*="css"], [data-testid="stApp"] {font-family:'DM Sans',sans-serif!important;}
[data-testid="stAppViewContainer"] {background:radial-gradient(ellipse 750px 370px at 75% -9%,rgba(92,105,239,.17),transparent 78%),#0b1221;color:#eaf0ff;}
.block-container {padding-top:2.3rem;padding-bottom:3rem;max-width:1510px;}
h1,h2,h3,h4,[data-testid="stHeadingWithActionElements"] {font-family:'Manrope',sans-serif!important;letter-spacing:-.035em!important;}
h1 {font-weight:800!important;font-size:2.25rem!important;}
h2 {font-weight:750!important;} h3 {font-weight:700!important;}
p, label, .stCaption {letter-spacing:.01em;}
[data-testid="stSidebar"] {background:#101a2c!important;border-right:1px solid #243251!important;}
[data-testid="stSidebar"] h2 {font-family:'Manrope',sans-serif!important;color:#f1f5ff!important;}
[data-testid="stSidebar"] [data-baseweb="select"]>div, [data-testid="stSidebar"] [data-baseweb="input"]>div {background:#0c1525!important;border-color:#314261!important;border-radius:11px!important;}
[data-baseweb="tag"] {background:#263d78!important;color:#dfe9ff!important;border-radius:7px!important;}
[data-baseweb="tag"] span {color:#e8efff!important;}
[data-baseweb="tag"] svg {fill:#e8efff!important;}
[data-testid="stMetric"] {background:linear-gradient(148deg,#192740 0%,#121d31 100%)!important;border:1px solid #2a3b5b!important;border-radius:18px!important;padding:20px 19px!important;box-shadow:0 12px 34px rgba(0,0,0,.17);min-height:121px;}
[data-testid="stMetricLabel"] {color:#a4b5d1!important;font-size:.84rem!important;}
[data-testid="stMetricValue"] {color:#f5f8ff!important;font-family:'Manrope',sans-serif!important;font-size:1.65rem!important;font-weight:800!important;letter-spacing:-.05em!important;}
[data-testid="stMetric"]:first-child {border-top:2px solid #88a8ff!important;}
[data-testid="stTabs"] [data-baseweb="tab-list"] {gap:9px;border-bottom:1px solid #273754;padding-bottom:9px;}
[data-testid="stTabs"] [data-baseweb="tab"] {border-radius:11px!important;color:#a5b8d5!important;padding:10px 16px!important;font-weight:700!important;background:#152138!important;}
[data-testid="stTabs"] [aria-selected="true"] {background:#2c4174!important;color:#eff4ff!important;}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {background:#9cb4ff!important;}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:#263856!important;border-radius:15px!important;}
[data-testid="stDataFrame"] {border:1px solid #2b3e60;border-radius:13px;overflow:hidden;}
[data-testid="stAlert"] {background:rgba(65,85,136,.18)!important;border:1px solid #3a4c79!important;border-radius:13px!important;color:#d4e1ff!important;}
[data-testid="stExpander"] {background:#111d31!important;border:1px solid #2a3b58!important;border-radius:13px!important;}
[data-testid="stDownloadButton"] button {background:linear-gradient(100deg,#647ff4,#497cd3)!important;color:white!important;border:0!important;border-radius:11px!important;font-weight:700!important;padding:11px 21px!important;}
input, [data-baseweb="input"] {border-radius:11px!important;}
.hero-eyebrow {color:#97b7ff;font-size:.77rem;font-weight:800;letter-spacing:.19em;text-transform:uppercase;margin-bottom:9px;}
.hero-title {font-family:'Manrope',sans-serif;font-size:clamp(2rem,3vw,3.05rem);font-weight:800;line-height:1.15;letter-spacing:-.055em;color:#f8faff;margin:0;}
.hero-title span {background:linear-gradient(92deg,#a8baff,#70d8ef);background-clip:text;-webkit-background-clip:text;color:transparent;}
.hero-sub {color:#a2afc7;font-size:1rem;margin:13px 0 23px;}
.hero-bar {height:4px;width:90px;border-radius:10px;background:linear-gradient(90deg,#718afa,#52c7dc);margin-bottom:20px;}
.footer-note {color:#8093b3;font-size:.78rem;margin-top:25px;}
@media(max-width:900px){.block-container{padding-top:1.4rem}.hero-title{font-size:2rem}}
</style>""", unsafe_allow_html=True)


REQUIRED_COLUMNS = [
    'Product_ID',
    'Product_Name',
    'Brand',
    'Category',
    'Competitor',
    'Date',
    'Price',
    'Original_Price',
    'Discount_Percent',
    'Rating',
    'Review_Count',
    'Units_Sold',
    'Revenue'
]

NUMERIC_COLUMNS = [
    'Price',
    'Original_Price',
    'Discount_Percent',
    'Rating',
    'Review_Count',
    'Units_Sold',
    'Revenue'
]

def prepare_data(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}"
        )

    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    if df.empty:
        raise ValueError("The uploaded dataset contains no records.")

    if df['Date'].notna().sum() == 0:
        raise ValueError("The dataset does not contain valid dates.")

    if df['Price'].notna().sum() == 0:
        raise ValueError("The dataset does not contain valid price values.")

    return df


def validate_dataset(df):
    missing_by_column = df.isna().sum()
    missing_cells = int(missing_by_column.sum())

    duplicate_rows = int(df.duplicated().sum())

    duplicate_observations = int(
        df.duplicated(
            subset=['Product_ID', 'Competitor', 'Date']
        ).sum()
    )

    invalid_dates = int(df['Date'].isna().sum())

    invalid_prices = int((
        (df['Price'].notna() & (df['Price'] <= 0))
        |
        (df['Original_Price'].notna() & (df['Original_Price'] <= 0))
    ).sum())

    invalid_discounts = int((
        df['Discount_Percent'].notna()
        & ~df['Discount_Percent'].between(0, 100)
    ).sum())

    invalid_ratings = int((
        df['Rating'].notna()
        & ~df['Rating'].between(0, 5)
    ).sum())

    report = {
        'Missing cells': missing_cells,
        'Duplicate rows': duplicate_rows,
        'Repeated product observations': duplicate_observations,
        'Invalid dates': invalid_dates,
        'Non-positive prices': invalid_prices,
        'Invalid discounts': invalid_discounts,
        'Invalid ratings': invalid_ratings
    }

    return report, missing_by_column[missing_by_column > 0]


@st.cache_data(show_spinner=False)
def load_data(path: Path):
    return prepare_data(pd.read_csv(path))



# ==========================================
# DATASET MANAGEMENT AND CSV UPLOAD
# ==========================================

st.sidebar.markdown("### | Dataset Management")

uploaded_file = st.sidebar.file_uploader(
    "Upload your dataset",
    type=["csv"],
    help="Upload a CSV containing the required product pricing columns."
)
is_custom_dataset = uploaded_file is not None

if uploaded_file is not None:
    try:
        uploaded_df = pd.read_csv(uploaded_file)
        df = prepare_data(uploaded_df)

        st.sidebar.success("Custom dataset loaded successfully!")
        st.sidebar.caption("Source: Uploaded CSV")

    except Exception as e:
        st.sidebar.error(f"Unable to load dataset: {e}")
        st.stop()

else:
    if not DATA.exists():
        st.error(
            f"Default dataset missing: {DATA}. "
            "Please upload a valid CSV dataset."
        )
        st.stop()

    try:
        df = load_data(DATA)
        st.sidebar.info("Using the default project dataset.")
    except Exception as e:
        st.error(f"Unable to load default dataset: {e}")
        st.stop()

st.sidebar.caption(f"Total rows: {len(df):,}")
st.sidebar.caption(f"Total columns: {len(df.columns)}")

with st.sidebar.expander("Preview selected dataset"):
    st.dataframe(df.head(5), use_container_width=True)

st.markdown("""<div class="hero-eyebrow">BEYOND THE NUMBERS / ANALYTICS WORKSPACE</div>
<h1 class="hero-title">Pricing <span>Intelligence.</span></h1>
<div class="hero-sub">Product pricing &amp; competitor analysis | Interactive analytics dashboard</div>
<div class="hero-bar"></div>""", unsafe_allow_html=True)
st.info('**SIMULATED DATA** | Educational project. Product observations, sales, revenue and business insights are synthetic, not live market results.')
# ==========================================
# DATASET QUALITY VALIDATION REPORT
# ==========================================

validation_report, missing_columns_report = validate_dataset(df)

with st.expander("Dataset Quality Report", expanded=False):

    st.caption(
        "Automatic quality checks for the currently selected dataset. "
        "No records are automatically deleted or modified."
    )

    quality_columns = st.columns(4)

    for index, (label, value) in enumerate(validation_report.items()):
        with quality_columns[index % 4]:
            st.metric(label, f"{value:,}")

    if any(validation_report.values()):
        st.warning(
            "Potential data quality issues detected. "
            "Review the results before using this dataset."
        )
    else:
        st.success("Excellent! No data quality issues detected.")

    if not missing_columns_report.empty:
        st.markdown("#### Missing values by column")

        missing_table = (
            missing_columns_report
            .rename("Missing Values")
            .rename_axis("Column")
            .reset_index()
        )

        st.dataframe(
            missing_table,
            use_container_width=True,
            hide_index=True
        )
st.sidebar.markdown('### | Explore data')
st.sidebar.caption('Use the controls to refine every metric and interactive chart.')
selected_categories = st.sidebar.multiselect('Categories', sorted(df['Category'].dropna().unique()), default=sorted(df['Category'].dropna().unique()))
selected_competitors = st.sidebar.multiselect('Competitors', sorted(df['Competitor'].dropna().unique()), default=sorted(df['Competitor'].dropna().unique()))
selected_brands = st.sidebar.multiselect('Brands', sorted(df['Brand'].dropna().unique()), default=sorted(df['Brand'].dropna().unique()))
valid_dates = df['Date'].dropna()
if valid_dates.empty:
    st.error('No valid dates found in dataset.'); st.stop()
# The dataset has monthly snapshots only (not daily records). Restrict
# the range control to dates that actually exist, so arbitrary calendar dates
# cannot accidentally leave the dashboard without observations.
available_dates = sorted(valid_dates.dt.normalize().drop_duplicates().dt.date.tolist())
from_date, to_date = st.sidebar.select_slider(
    'Observation date range',
    options=available_dates,
    value=(available_dates[0], available_dates[-1]),
    format_func=lambda date: date.strftime('%b %Y'),
    help='Choose the first and last observation months to include. Both endpoints are included.',
)
st.sidebar.caption(f'Including snapshots from {from_date:%b %Y} through {to_date:%b %Y}.')

f = df[
    df['Category'].isin(selected_categories)
    & df['Competitor'].isin(selected_competitors)
    & df['Brand'].isin(selected_brands)
    & df['Date'].dt.normalize().between(pd.Timestamp(from_date), pd.Timestamp(to_date))
].copy()
if f.empty:
    st.info('No observations match these category, competitor, brand and date selections. Try broadening the filters.')
    st.stop()

currency = lambda x: f'\u20b9{x:,.0f}'
num = lambda x: f'{x:,.0f}'
metrics = st.columns(5)
metrics[0].metric('Products',num(f['Product_ID'].nunique()))
metrics[1].metric('Observations',num(len(f)))
metrics[2].metric('Average price',currency(f['Price'].mean()))
metrics[3].metric('Average discount',f"{f['Discount_Percent'].mean():.1f}%")
metrics[4].metric('Average rating',f"{f['Rating'].mean():.2f} / 5")

st.markdown('')
tab1,tab2,tab3,tab4 = st.tabs(['Overview', 'Competitor Analysis', 'Trends & Relationships', 'Product Explorer'])
with tab1:
    a,b=st.columns(2)
    with a:
        st.subheader('Average price by category')
        t=f.groupby('Category',as_index=False)['Price'].mean().sort_values('Price',ascending=False)
        st.bar_chart(t.set_index('Category')['Price'], y_label='Average price (\u20b9)')
    with b:
        st.subheader('Average price by competitor')
        t=f.groupby('Competitor',as_index=False)['Price'].mean().sort_values('Price',ascending=False)
        st.bar_chart(t.set_index('Competitor')['Price'], y_label='Average price (\u20b9)')
    a,b=st.columns(2)
    with a:
        st.subheader('Average discount by category')
        st.bar_chart(f.groupby('Category')['Discount_Percent'].mean(),y_label='Discount (%)')
    with b:
        st.subheader('Simulated revenue by category')
        st.bar_chart(f.groupby('Category')['Revenue'].sum(), y_label='Simulated revenue (\u20b9)')
with tab2:
    st.subheader('Competitor scorecard')
    score=f.groupby('Competitor').agg(Observations=('Price','size'),Products=('Product_ID','nunique'),Avg_Price=('Price','mean'),Avg_Discount_Pct=('Discount_Percent','mean'),Avg_Rating=('Rating','mean'),Simulated_Revenue=('Revenue','sum')).reset_index()
    st.dataframe(score.style.format({'Avg_Price':'\u20b9{:,.2f}','Avg_Discount_Pct':'{:.2f}%','Avg_Rating':'{:.2f}','Simulated_Revenue':'\u20b9{:,.0f}'}),use_container_width=True,hide_index=True)
    st.subheader('Category by competitor average prices')
    pivot=f.pivot_table(index='Category',columns='Competitor',values='Price',aggfunc='mean')
    st.dataframe(pivot.style.format('\u20b9{:,.0f}').background_gradient(cmap='Blues',axis=None),use_container_width=True)
    st.caption('Comparisons reflect filtered synthetic observations, not live competitor prices.')
with tab3:
    monthly=f.assign(Month=f['Date'].dt.to_period('M').astype(str)).groupby('Month',as_index=True).agg(Avg_Price=('Price','mean'),Avg_Discount=('Discount_Percent','mean'),Units_Sold=('Units_Sold','sum'),Revenue=('Revenue','sum'))
    a,b=st.columns(2)
    with a:
        st.subheader('Average price trend')
        st.line_chart(monthly['Avg_Price'], y_label='Average price (\u20b9)')
    with b:
        st.subheader('Average discount trend')
        st.line_chart(monthly['Avg_Discount'],y_label='Average discount (%)')
    a,b=st.columns(2)
    with a:
        st.subheader('Simulated units sold trend')
        st.line_chart(monthly['Units_Sold'],y_label='Units sold (simulated)')
    with b:
        st.subheader('Simulated revenue trend')
        st.line_chart(monthly['Revenue'], y_label='Revenue (\u20b9, simulated)')
    st.subheader('Price and rating relationship')
    st.scatter_chart(f,x='Price',y='Rating',color='Category',size=None)
    st.caption('Associations in simulated data do not establish causation or real-world price sensitivity.')
with tab4:
    st.subheader('Search and explore products')
    term=st.text_input('Search product name or ID',placeholder='e.g. Headphones or P0001')
    view=f.copy()
    if term.strip():
        mask=view['Product_Name'].astype(str).str.contains(term,case=False,regex=False,na=False)|view['Product_ID'].astype(str).str.contains(term,case=False,regex=False,na=False)
        view=view[mask]
    columns=['Date','Product_ID','Product_Name','Category','Brand','Competitor','Price','Original_Price','Discount_Percent','Rating','Review_Count','Units_Sold','Revenue']
    st.caption(f'{len(view):,} matching observations')
    st.dataframe(view[columns].sort_values('Date',ascending=False),use_container_width=True,hide_index=True)
    st.download_button('Download filtered observations (CSV)',view[columns].to_csv(index=False).encode('utf-8'),file_name='filtered_product_observations.csv',mime='text/csv')

if is_custom_dataset:
    st.info(
        "The 18 original static charts belong to the default "
        "project dataset. They are hidden because you are using "
        "a custom dataset. The interactive charts above reflect "
        "your uploaded data."
    )
else:
    with st.expander('View all 18 original static charts'):
        imgs = sorted(CHARTS.glob('*.png')) if CHARTS.exists() else []

        if not imgs:
            st.info('No PNG charts found in outputs/visualizations.')

        for i in range(0, len(imgs), 2):
            cs = st.columns(2)
            for j, p in enumerate(imgs[i:i+2]):
                with cs[j]:
                    st.image(
                        str(p),
                        caption=p.stem.replace('_', ' ').title(),
                        use_container_width=True
                    )
st.markdown('<div class="footer-note">PRICING INTELLIGENCE  |  DATA SOURCE: CLEANED_DATA.CSV  |  SYNTHETIC EDUCATIONAL DATA  |  FILTERS RECALCULATE LIVE</div>', unsafe_allow_html=True)


