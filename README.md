# WRDS Financial Benchmarking Tool

## Project Overview
This project develops a financial benchmarking tool for software and related technology service firms using WRDS Compustat annual data. The notebook builds a full workflow for data retrieval, cleaning, variable construction, outlier treatment, industry-level analysis, and firm-level benchmarking. The Streamlit app turns the final outputs into an interactive tool for exploring industry trends and comparing an individual company with the broader benchmark.

The analysis focuses on firms with historical SIC codes between **7370 and 7379**, which broadly represent software and related technology services. The main analysis period is **2015 to 2024**, while **2014** is additionally included to construct lag-based growth metrics.

## Product Purpose
The purpose of this project is to transform raw WRDS financial statement data into a simple and reusable benchmarking product. It helps users examine industry-wide financial patterns over time and compare a selected company with the industry benchmark.

## Research Question
How has the financial performance of software and related technology service firms changed from 2015 to 2024, and how does an individual firm compare with the overall industry benchmark?

## Intended Users
This project is designed for business students, beginner investors, and users who want a simple tool to compare a firm’s financial performance with broader industry patterns.

## Data Source
The data are retrieved from **WRDS Compustat Annual Fundamentals (`comp.funda`)**. The project uses annual firm-level accounting data such as net income, total assets, total revenue, total equity, company identifiers, and company names.

To improve consistency, the notebook applies standard Compustat filters:

- `indfmt = 'INDL'`
- `datafmt = 'STD'`
- `popsrc = 'D'`
- `consol = 'C'`

## Variables and Financial Measures

### Key Variables
The notebook extracts and prepares the following variables:

- `gvkey`: firm identifier  
- `datadate`: reporting date  
- `fyear`: fiscal year  
- `tic`: ticker symbol  
- `conm`: company name  
- `sich`: historical SIC code  
- `ni`: net income  
- `at`: total assets  
- `sale`: total revenue  
- `seq`: total equity  

### Financial Metrics
The project constructs eight accounting-based indicators:

- **ROA** = net income / total assets  
- **ROE** = net income / total equity  
- **Profit Margin** = net income / revenue  
- **Turnover** = revenue / total assets  
- **Leverage** = total assets / total equity  
- **Equity Ratio** = total equity / total assets  
- **Revenue Growth** = current revenue / lagged revenue - 1  
- **Asset Growth** = current total assets / lagged total assets - 1  

These measures capture profitability, efficiency, capital structure, and growth.

## Methodology

### 1. Data Retrieval
The notebook connects to WRDS and retrieves annual firm-level observations for companies with historical SIC codes from **7370 to 7379**.

### 2. Initial Data Checks and Preparation
After extraction, the notebook:

- renames variables for readability  
- checks sample size and year coverage  
- verifies that each firm-year observation is unique  
- confirms that key accounting variables are available for the main analysis  

### 3. Construction of Financial Metrics
The notebook constructs the eight financial metrics listed above. For ratio measures, values are calculated only when the denominator is economically valid, so some measures such as ROE, leverage, and growth metrics remain unavailable for some firm-years.

### 4. Outlier Treatment
Because accounting data often contain extreme values, the project applies **winsorization at the 1st and 99th percentiles** for all eight metrics. This reduces the influence of unusually large or small observations while preserving the sample.

### 5. Sample Design
The project uses **two related samples**.

#### Full Sample
The **full cleaned and winsorized sample** is used for:

- industry-level yearly summaries  
- trend charts  
- boxplots and other descriptive visualisations  

This keeps as many valid firm-year observations as possible for industry analysis.

#### Balanced Benchmark Sample
A stricter **balanced sample** is created for long-horizon firm benchmarking. A company is kept only if it has complete observations for the following **three core metrics** in **every fiscal year from 2015 to 2024**:

- ROA  
- Profit Margin  
- Turnover  

Other metrics such as ROE, leverage, equity ratio, revenue growth, and asset growth are reported when available, but they are **not used as hard screening requirements**. This improves comparability across firms while avoiding excessive sample loss.

## Main Outputs

### Industry-Level Outputs
The notebook produces:

- yearly mean, median, and valid observation count for each metric  
- industry trend charts over time  
- yearly distribution charts  
- a latest-year benchmark comparison across key metrics  

### Firm-Level Outputs
The notebook also creates a company benchmarking function that:

- takes a ticker as input  
- compares the selected firm with industry mean and median  
- reports whether the firm performs above or below the benchmark  
- visualises multi-year company performance against the industry  

## Streamlit App
The project includes an interactive Streamlit app (`app.py`) built from the exported CSV files.

### App Structure
The app contains the following sections:

- **Home**: project summary, sample information, and available metrics  
- **Industry Dashboard**: industry mean, median, and yearly distributions  
- **Company Benchmark**: comparison of one company against industry benchmarks  
- **Data Overview**: inspection of the exported datasets used in the app  

### What the App Does
The app allows users to:

- explore industry trends from **2015 to 2024**  
- select metrics for visual analysis  
- input a company ticker and compare the company with the industry  
- inspect the benchmark tables behind the charts  

## Exported Files
The notebook exports the following files for the app:

- `full_sample.csv`: full cleaned and winsorized sample used for industry-level analysis  
- `balanced_data.csv`: stricter balanced sample used for company benchmarking  
- `industry_benchmark.csv`: yearly industry benchmark table used in the app  

## File Structure

```text
WRDS_Financial_Benchmarking_Tool.ipynb
app.py
full_sample.csv
balanced_data.csv
industry_benchmark.csv
requirements.txt
README.md
```

## How to Run the Project

### Run the Notebook

```bash
jupyter notebook
```

The notebook requires WRDS access for data retrieval.

### Run the Streamlit App

```bash
streamlit run app.py
```

## Limitations

This project has several limitations.

First, the industry definition is based on historical SIC codes 7370 to 7379, so it may not include every firm in the broader technology sector.

Second, the analysis uses annual accounting data only, so short-term within-year changes are not captured.

Third, some metrics remain unavailable for certain firm-years when denominators are zero, negative, or otherwise invalid, especially for ROE, leverage, and lag- based growth measures.

Fourth, winsorization improves stability but may reduce the visibility of some extreme yet economically meaningful observations.

Finally, the app compares a selected firm with industry mean and median, but it does not yet include more advanced features such as peer clustering, percentile ranking, or size-based segmentation.

## Conclusion

This project shows how Python and WRDS can be combined to transform raw Compustat financial data into a practical benchmarking product. The notebook builds the full analytical workflow, while the Streamlit app makes the results easier to explore and interpret. Together, they provide a simple tool for analysing industry performance and comparing an individual firm with the broader benchmark over time.

## AI Use Disclosure

Generative AI was used as a support tool during this project. It assisted with improving explanations, refining markdown text, and reviewing parts of the code structure. All final analysis design, metric definitions, data processing decisions, and output checks were reviewed and validated by the student.
