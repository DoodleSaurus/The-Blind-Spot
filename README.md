# The Blind Spot - Gender Equality Transparency Dashboard

## 📊 Overview

**The Blind Spot** is an innovative data analysis project that flips traditional gender equality reporting on its head. Instead of analyzing what companies *do* report about gender metrics, we focus on what they *don't* report. By quantifying missing data in corporate sustainability reports, we transform information gaps into transparency indicators using our proprietary **Omission Severity Score (OSS)** system.

> "What isn't measured, isn't managed. What isn't communicated, often doesn't exist. We make the invisible visible."

## 🎯 Core Concept

While most analyses examine present data (pay gaps, STEM percentages, etc.), **The Blind Spot** examines absent data. We've developed a comprehensive checklist of 50+ KPIs derived from European ESG directives and international gender equality standards, assigning severity weights to each missing metric.

## ✨ Features

### **Interactive Dashboard**
- **Multi-Tab Analysis**: 9 different visualization perspectives
- **Real-time Filtering**: Filter by year, sector, company type, severity level
- **Comparative Analysis**: Quotate vs. Non-Quotate company comparisons
- **Trend Tracking**: Multi-year transparency evolution tracking
- **KPI Breakdown**: Sunburst and radar visualizations of missing metrics
- **Export Ready**: All data exportable for further analysis

### **Visualizations Include:**
- **OSS Score Distribution**: Bar charts with severity color coding
- **Severity Level Distribution**: Interactive pie charts
- **Sector Comparisons**: Box plots and strip charts
- **Trend Analysis**: Line graphs with change metrics
- **KPI Heatmaps**: Missing rate visualizations
- **Radar Charts**: Top missing KPI patterns
- **Data Tables**: Sortable, filterable data tables

### **Automated Scoring System**
- **Binary Collection**: KPI Present = 0, Missing = 1
- **Weighted Severity**: Different weights for different KPIs (**1-5 points**)
- **OSS Calculation**: Σ (Missing KPI × Weight), Max Score = 185
- **Severity Classification**: 6 levels from "Trasparente" to "Estrema"

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
```bash
# Clone the repository
git clone [repository-url]

# Navigate to project directory
cd the-blind-spot

# Install dependencies
pip install -r requirements.txt

# Run the application
python start.py
```

### Required Python Packages:
- `pandas>=2.0.0`
- `plotly>=5.18.0`
- `dash>=2.14.0`
- `dash-bootstrap-components>=1.5.0`
- `openpyxl>=3.1.0`

## 📁 Project Structure

```
the-blind-spot/
├── start.py              # Entry point with animated introduction
├── analyzer.py           # Main dashboard application
├── requirements.txt      # Python dependencies
├── datasets/             # Excel data files
│   ├── quotate/         # Listed companies data
│   └── non_quotate/     # Non-listed companies data
├── README.md            # This file
└── assets/              # Static assets (logos, styles)
```

## 📊 Data Structure

### Excel File Format
The dashboard reads specially formatted Excel files:
- **Column A**: Category (e.g., Board & Governance)
- **Column B**: KPI Name (e.g., "% women in Board")
- **Column C**: Weight (**1-5**)
- **Column D+**: Company columns (0 = present, 1 = missing)
- **Adjacent OSS Columns**: Automatically calculated OSS scores

### Sample Companies Analyzed
- **Quotate**: Enel, Eni, STMicroelectronics, Leonardo, Intesa Sanpaolo, UniCredit, Stellantis, Ferrari, etc.
- **Non-Quotate**: AlmavivA, Engineering, Fastweb, Esselunga, Coop Italia, Ferrero, Barilla, FS Italiane, etc.

## 🎨 Dashboard Tabs

1. **About**: Project methodology and OSS explanation
2. **Overview (OSS)**: Main OSS score distribution
3. **Quotate Gap**: Comparison between listed and non-listed companies
4. **Severity Analysis**: Distribution of severity levels
5. **Sector Comparison**: Cross-sector analysis
6. **Trend Analysis**: Multi-year transparency evolution
7. **KPI Breakdown**: Category and KPI-level missing rates
8. **KPI Radar**: Visual pattern of most missing KPIs
9. **Data Table**: Raw data table with sorting and filtering

## 🔍 Methodology

### 1. **KPI Checklist Development**
50+ KPIs across 13 categories:
- Board & Governance
- Management & Leadership
- Total Workforce
- Pay Equity
- STEM & Strategic Roles
- Inclusion Policies
- Training & Development
- Work-Life Balance
- Inclusive Culture
- Supplier Diversity
- Community Impact
- Communication & Transparency
- Risk & Compliance

### 2. **Severity Weighting System**
Each KPI receives a weight based on importance:
- **Weight 1**: Standard reporting items
- **Weight 2-4**: Increasing importance and impact
- **Weight 5**: Critical equality indicators

### 3. **OSS Calculation**
```
OSS = Σ (Missing KPI Indicator × Weight)
```
- **Minimum**: 0 (perfect transparency)
- **Maximum**: 185 (no transparency)

### 4. **Severity Classification**
| OSS Range | Percentage | Severity | Interpretation |
|-----------|------------|----------|----------------|
| 0-31 | 0-16.67% | Trasparente | Minimal omissions |
| 32-62 | 16.68-33.33% | Bassa | Low omission level |
| 63-93 | 33.34-50% | Moderata | Several important KPIs missing |
| 94-124 | 50.01-66.67% | Grave | Significant omissions |
| 125-155 | 66.68-83.33% | Critica | Fundamental KPIs missing |
| 156-185 | 83.34-100% | Estrema | Almost all critical areas omitted |


The project includes entertaining elements:
- **Animated Intro**: "Hacking" animation with humorous disclaimers
- **Progress Animations**: Loading spinners, matrix rain, glitch effects
- **Interactive Feedback**: Real-time filtering and visual feedback
- **Achievement Tracking**: Implicit "improvement tracking" system

## 🎯 Target Audience

1. **Investors**: ESG-focused investment decisions
2. **Regulators**: Identifying reporting gaps and compliance issues
3. **Activists**: Advocacy and corporate accountability campaigns
4. **Companies**: Benchmarking and improvement tracking
5. **Researchers**: Academic studies on corporate transparency

## 🔧 Technical Implementation

- **Backend**: Python with Pandas for data processing
- **Frontend**: Dash (Plotly) for interactive visualizations
- **Styling**: Custom CSS with Inter font and modern design system
- **Data Processing**: Automated Excel file parsing with dynamic column detection
- **Statistical Analysis**: Bootstrap methods for significance testing

## 📈 Key Insights Delivered

- **Transparency Rankings**: Companies ranked by OSS scores
- **Sector Benchmarks**: Industry-wide transparency comparisons
- **Trend Identification**: Improving vs. worsening companies over time
- **Gap Analysis**: Most commonly omitted KPIs across industries
- **Compliance Tracking**: Alignment with EU directives and ESG standards

## 🚧 Limitations & Future Work

- **Current**: Focus on Italian companies
- **Future**: Expand to European/international companies
- **Current**: Manual/automated Excel processing
- **Future**: API integration with corporate databases
- **Current**: Static annual reporting
- **Future**: Real-time data feeds and alerts

## 🤝 Team & Acknowledgments

Developed with ❤️ by the **Ingenium** team.

**Special Thanks To:**
- All contributing companies for their (sometimes missing) data
- The open-source community for Dash and Plotly
- Countless cups of coffee ☕

## 📄 License

This project is developed for educational and research purposes. Data belongs to respective companies and should be used in accordance with their reporting policies.

---

**Remember**: This tool doesn't measure gender equality—it measures transparency *about* gender equality. The absence of data is itself a powerful data point.
