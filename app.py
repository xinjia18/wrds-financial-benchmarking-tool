import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Financial Benchmarking App",
    layout="wide"
)

# -----------------------------
# Configuration
# -----------------------------
METRIC_LABELS = {
    'roa': 'ROA',
    'roe': 'ROE',
    'profit_margin': 'Profit Margin',
    'turnover': 'Turnover',
    'leverage': 'Leverage',
    'equity_ratio': 'Equity Ratio',
    'revenue_growth': 'Revenue Growth',
    'asset_growth': 'Asset Growth'
}

PERCENT_METRICS = {
    'roa', 'roe', 'profit_margin',
    'equity_ratio', 'revenue_growth', 'asset_growth'
}

KEY_METRICS = [
    'roa', 'roe', 'profit_margin', 'turnover',
    'leverage', 'equity_ratio', 'revenue_growth', 'asset_growth'
]


# -----------------------------
# Helpers
# -----------------------------
@st.cache_data
def load_data():
    balanced = pd.read_csv("balanced_data.csv")
    full = pd.read_csv("full_sample.csv")
    industry = pd.read_csv("industry_benchmark.csv")

    # Basic cleanup
    for df in [balanced, full, industry]:
        if 'fyear' in df.columns:
            df['fyear'] = pd.to_numeric(df['fyear'], errors='coerce').astype('Int64')

    numeric_cols_balanced = [
        'roa', 'roe', 'profit_margin', 'turnover',
        'leverage', 'equity_ratio', 'revenue_growth', 'asset_growth'
    ]
    for col in numeric_cols_balanced:
        if col in balanced.columns:
            balanced[col] = pd.to_numeric(balanced[col], errors='coerce')
        if col in full.columns:
            full[col] = pd.to_numeric(full[col], errors='coerce')

    for metric in KEY_METRICS:
        mean_col = f"{metric}_mean"
        median_col = f"{metric}_median"
        if mean_col in industry.columns:
            industry[mean_col] = pd.to_numeric(industry[mean_col], errors='coerce')
        if median_col in industry.columns:
            industry[median_col] = pd.to_numeric(industry[median_col], errors='coerce')

    return balanced, full, industry


def metric_to_display(metric, series):
    if metric in PERCENT_METRICS:
        return series * 100
    return series


def format_value(metric, value):
    if pd.isna(value):
        return "N/A"
    if metric in PERCENT_METRICS:
        return f"{value * 100:.2f}%"
    return f"{value:.2f}"


def get_company_options(df):
    temp = (
        df[['ticker', 'company_name']]
        .dropna(subset=['ticker'])
        .drop_duplicates()
        .sort_values('ticker')
        .copy()
    )
    temp['display'] = temp.apply(
        lambda x: f"{x['ticker']} | {x['company_name']}" if pd.notna(x['company_name']) else x['ticker'],
        axis=1
    )
    return temp


def build_company_summary(company_df, industry_df):
    summary_rows = []

    for metric in KEY_METRICS:
        mean_col = f"{metric}_mean"
        median_col = f"{metric}_median"

        temp = company_df[['fyear', metric]].merge(
            industry_df[['fyear', mean_col, median_col]],
            on='fyear',
            how='left'
        ).dropna()

        if temp.empty:
            continue

        above_mean = (temp[metric] > temp[mean_col]).sum()
        above_median = (temp[metric] > temp[median_col]).sum()
        total_years = len(temp)

        latest_row = temp.sort_values('fyear').iloc[-1]

        summary_rows.append({
            'Metric': METRIC_LABELS[metric],
            'Years Above Mean': int(above_mean),
            'Years Above Median': int(above_median),
            'Comparable Years': int(total_years),
            'Latest vs Mean': 'Above' if latest_row[metric] > latest_row[mean_col] else 'Below',
            'Latest vs Median': 'Above' if latest_row[metric] > latest_row[median_col] else 'Below'
        })

    return pd.DataFrame(summary_rows)


def build_percentile_df(company_df, full_df, metric):
    rows = []

    for _, row in company_df[['fyear', metric]].dropna().iterrows():
        year = row['fyear']
        firm_value = row[metric]

        dist = full_df.loc[full_df['fyear'] == year, metric].dropna()

        if len(dist) > 0:
            percentile = (dist <= firm_value).mean() * 100
            rows.append({
                'fyear': int(year),
                'percentile': percentile
            })

    return pd.DataFrame(rows)


def format_company_table(df):
    display_df = df.copy()

    for metric in KEY_METRICS:
        if metric in display_df.columns:
            if metric in PERCENT_METRICS:
                display_df[metric] = display_df[metric].apply(
                    lambda x: f"{x*100:.2f}%" if pd.notna(x) else ""
                )
            else:
                display_df[metric] = display_df[metric].apply(
                    lambda x: f"{x:.2f}" if pd.notna(x) else ""
                )

    return display_df


def format_industry_snapshot(df, year):
    row = df[df['fyear'] == year]
    if row.empty:
        return pd.DataFrame()

    row = row.iloc[0]
    output = []

    for metric in KEY_METRICS:
        output.append({
            'Metric': METRIC_LABELS[metric],
            'Industry Mean': format_value(metric, row.get(f'{metric}_mean', np.nan)),
            'Industry Median': format_value(metric, row.get(f'{metric}_median', np.nan))
        })

    return pd.DataFrame(output)


# -----------------------------
# Load data
# -----------------------------
balanced_data, full_sample, industry_benchmark = load_data()

latest_year = int(industry_benchmark['fyear'].dropna().max())
all_years = sorted(industry_benchmark['fyear'].dropna().astype(int).unique().tolist())

company_options_df = get_company_options(balanced_data)
company_display_list = company_options_df['display'].tolist()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Navigation")

page = st.sidebar.selectbox(
    "Choose a page",
    ["Home", "Industry Dashboard", "Company Benchmark", "Data Overview"]
)

st.sidebar.markdown("---")

if page == "Industry Dashboard":
    selected_metric = st.sidebar.selectbox(
        "Select a metric",
        KEY_METRICS,
        format_func=lambda x: METRIC_LABELS[x]
    )
    selected_year = st.sidebar.selectbox(
        "Select a year",
        all_years,
        index=len(all_years) - 1
    )

elif page == "Company Benchmark":
    selected_company_display = st.sidebar.selectbox(
        "Select a company",
        company_display_list
    )
    selected_ticker = selected_company_display.split(" | ")[0]
    selected_metric = st.sidebar.selectbox(
        "Select a metric",
        KEY_METRICS,
        format_func=lambda x: METRIC_LABELS[x]
    )

# -----------------------------
# Home Page
# -----------------------------
if page == "Home":
    st.title("Financial Benchmarking App")
    st.markdown(
        """
        This app benchmarks software and related technology service firms using WRDS Compustat annual data from 2015 to 2024.  
        It provides both industry-level trends and firm-level comparisons.
        """
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Full Sample Firms", f"{full_sample['gvkey'].nunique():,}")
    col2.metric("Balanced Firms", f"{balanced_data['gvkey'].nunique():,}")
    col3.metric("Analysis Years", f"{min(all_years)}–{max(all_years)}")
    col4.metric("Metrics Used", f"{len(KEY_METRICS)}")

    st.markdown("### Available Metrics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        - **ROA**: Return on Assets  
        - **ROE**: Return on Equity  
        - **Profit Margin**: Net income / revenue  
        - **Turnover**: Revenue / total assets
        """)

    with col2:
        st.markdown("""
        - **Leverage**: Total assets / total equity  
        - **Equity Ratio**: Total equity / total assets  
        - **Revenue Growth**: Year-over-year revenue growth  
        - **Asset Growth**: Year-over-year asset growth
        """)

    st.markdown("### App Structure")
    st.markdown(
        """
        - **Industry Dashboard**: explore industry mean, median, and yearly distributions  
        - **Company Benchmark**: compare one company with the industry over time  
        - **Data Overview**: inspect the exported datasets used by the app
        """
    )

# -----------------------------
# Industry Dashboard
# -----------------------------
elif page == "Industry Dashboard":
    st.title("Industry Dashboard")

    st.subheader(f"{METRIC_LABELS[selected_metric]}: Industry Trend")

    trend_df = industry_benchmark[['fyear', f'{selected_metric}_mean', f'{selected_metric}_median']].dropna().copy()
    trend_df['Mean'] = metric_to_display(selected_metric, trend_df[f'{selected_metric}_mean'])
    trend_df['Median'] = metric_to_display(selected_metric, trend_df[f'{selected_metric}_median'])

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend_df['fyear'],
        y=trend_df['Mean'],
        mode='lines+markers',
        name='Industry Mean'
    ))
    fig_trend.add_trace(go.Scatter(
        x=trend_df['fyear'],
        y=trend_df['Median'],
        mode='lines+markers',
        name='Industry Median'
    ))
    fig_trend.update_layout(
        xaxis_title="Fiscal Year",
        yaxis_title=METRIC_LABELS[selected_metric],
        height=450
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    latest_row = industry_benchmark[industry_benchmark['fyear'] == selected_year].iloc[0]
    selected_year_full = full_sample[full_sample['fyear'] == selected_year]

    year_metric_values = selected_year_full[selected_metric].dropna()

    col1.metric(
        f"{selected_year} Mean",
        format_value(selected_metric, latest_row[f'{selected_metric}_mean'])
    )
    col2.metric(
        f"{selected_year} Median",
        format_value(selected_metric, latest_row[f'{selected_metric}_median'])
    )
    col3.metric(
        f"{selected_year} Observations",
        f"{len(year_metric_values):,}"
    )

    st.subheader(f"{METRIC_LABELS[selected_metric]}: Distribution by Year")

    box_df = full_sample[['fyear', selected_metric]].dropna().copy()
    box_df['display_value'] = metric_to_display(selected_metric, box_df[selected_metric])

    fig_box = px.box(
        box_df,
        x='fyear',
        y='display_value',
        points=False
    )
    fig_box.update_layout(
        xaxis_title="Fiscal Year",
        yaxis_title=METRIC_LABELS[selected_metric],
        height=450
    )
    st.plotly_chart(fig_box, use_container_width=True)

    st.subheader(f"{selected_year}: Industry Snapshot")
    snapshot_df = format_industry_snapshot(industry_benchmark, selected_year)
    st.dataframe(snapshot_df, use_container_width=True)

# -----------------------------
# Company Benchmark
# -----------------------------
elif page == "Company Benchmark":
    st.title("Company Benchmark")

    company_df = balanced_data[balanced_data['ticker'] == selected_ticker].copy()
    company_name = company_df['company_name'].dropna().iloc[0] if company_df['company_name'].notna().any() else selected_ticker

    st.markdown(f"### {company_name} ({selected_ticker})")

    merged_df = company_df.merge(
        industry_benchmark,
        on='fyear',
        how='left'
    ).sort_values('fyear')

    metric_df = merged_df[['fyear', selected_metric, f'{selected_metric}_mean', f'{selected_metric}_median']].dropna().copy()
    metric_df['Company'] = metric_to_display(selected_metric, metric_df[selected_metric])
    metric_df['Industry Mean'] = metric_to_display(selected_metric, metric_df[f'{selected_metric}_mean'])
    metric_df['Industry Median'] = metric_to_display(selected_metric, metric_df[f'{selected_metric}_median'])

    if not metric_df.empty:
        latest_metric_row = metric_df.sort_values('fyear').iloc[-1]

        col1, col2, col3 = st.columns(3)
        col1.metric(
            f"Latest {METRIC_LABELS[selected_metric]}",
            format_value(selected_metric, latest_metric_row[selected_metric])
        )
        col2.metric(
            "Industry Mean",
            format_value(selected_metric, latest_metric_row[f'{selected_metric}_mean'])
        )
        col3.metric(
            "Industry Median",
            format_value(selected_metric, latest_metric_row[f'{selected_metric}_median'])
        )

    st.subheader(f"{METRIC_LABELS[selected_metric]}: Company vs Industry")

    fig_company = go.Figure()
    fig_company.add_trace(go.Scatter(
        x=metric_df['fyear'],
        y=metric_df['Company'],
        mode='lines+markers',
        name=selected_ticker
    ))
    fig_company.add_trace(go.Scatter(
        x=metric_df['fyear'],
        y=metric_df['Industry Mean'],
        mode='lines+markers',
        name='Industry Mean'
    ))
    fig_company.add_trace(go.Scatter(
        x=metric_df['fyear'],
        y=metric_df['Industry Median'],
        mode='lines+markers',
        name='Industry Median'
    ))
    fig_company.update_layout(
        xaxis_title="Fiscal Year",
        yaxis_title=METRIC_LABELS[selected_metric],
        height=450
    )
    st.plotly_chart(fig_company, use_container_width=True)

    st.subheader(f"{METRIC_LABELS[selected_metric]}: Percentile Rank Over Time")

    percentile_df = build_percentile_df(company_df, full_sample, selected_metric)

    if not percentile_df.empty:
        fig_pct = px.line(
            percentile_df,
            x='fyear',
            y='percentile',
            markers=True
        )
        fig_pct.update_layout(
            xaxis_title="Fiscal Year",
            yaxis_title="Percentile Rank",
            yaxis=dict(range=[0, 100]),
            height=400
        )
        st.plotly_chart(fig_pct, use_container_width=True)
    else:
        st.info("No percentile data available for the selected metric.")

    st.subheader("Performance Diagnostic Summary")
    summary_df = build_company_summary(company_df, industry_benchmark)
    st.dataframe(summary_df, use_container_width=True)

    st.subheader("Company Benchmark Table")
    benchmark_table = company_df[
        ['fyear', 'roa', 'roe', 'profit_margin', 'turnover',
         'leverage', 'equity_ratio', 'revenue_growth', 'asset_growth']
    ].sort_values('fyear')

    st.dataframe(format_company_table(benchmark_table), use_container_width=True)

# -----------------------------
# Data Overview
# -----------------------------
elif page == "Data Overview":
    st.title("Data Overview")

    st.markdown("### Exported Files Used by the App")
    file_info = pd.DataFrame({
        "File": ["balanced_data.csv", "full_sample.csv", "industry_benchmark.csv"],
        "Purpose": [
            "Firm-level benchmark data for selected companies",
            "Industry distribution data for boxplots and percentile analysis",
            "Industry mean and median benchmark data by year"
        ]
    })
    st.dataframe(file_info, use_container_width=True)

    st.markdown("### Preview: Balanced Data")
    st.dataframe(balanced_data.head(10), use_container_width=True)

    st.markdown("### Preview: Industry Benchmark")
    st.dataframe(industry_benchmark.head(10), use_container_width=True)

    st.markdown("### Dataset Summary")
    summary = pd.DataFrame({
        "Item": [
            "Full sample firms",
            "Balanced sample firms",
            "Full sample observations",
            "Balanced sample observations",
            "Year range"
        ],
        "Value": [
            full_sample['gvkey'].nunique(),
            balanced_data['gvkey'].nunique(),
            len(full_sample),
            len(balanced_data),
            f"{min(all_years)}–{max(all_years)}"
        ]
    })
    st.dataframe(summary, use_container_width=True)