import math
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import glob
import os
from rag_generator import BlindSpotRAG
import base64
import io
from flask import send_file
import uuid

# App configuration
external_stylesheets = [dbc.themes.FLATLY]
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
app.title = "The Blind Spot — Gender Equality Transparency"

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg: #f4f6f9;
                --surface: #ffffff;
                --surface-alt: #f8fafc;
                --text: #0b1220;
                --text-muted: #5b6475;
                --accent: #0f766e;
                --accent-soft: rgba(15,118,110,0.08);
                --border: #e5e7eb;
                --shadow: 0 12px 36px rgba(15,23,42,0.05);
                --radius: 12px;
            }
            body { background: radial-gradient(120% 120% at 12% 18%, #ffffff 0, #f4f6f9 45%, #e9edf3 100%); color: var(--text); font-family: 'Inter', sans-serif; letter-spacing: -0.15px; }
            a { color: var(--accent); }
            .elegant-card { background: var(--surface); border-radius: var(--radius); border: 1px solid var(--border); box-shadow: var(--shadow); transition: transform 0.08s ease, border-color 0.12s ease, box-shadow 0.12s ease; }
            .elegant-card:hover { transform: translateY(-2px); border-color: rgba(15,118,110,0.3); box-shadow: 0 16px 44px rgba(15,23,42,0.07); }
            .page-header{ background: var(--surface); padding: 26px 28px; border-radius: var(--radius); box-shadow: var(--shadow); border: 1px solid var(--border); }
            .header-title{ font-weight: 800; font-size: 2.0rem; letter-spacing: -0.35px; margin: 0; }
            .header-sub{ color: var(--text-muted); font-size: 0.98rem; margin-top: 6px; }
            .metric-title{ color: var(--text-muted); font-size: 0.82rem; margin-bottom: 6px; }
            .metric-value{ font-size: 1.6rem; font-weight: 800; margin-bottom: 4px; letter-spacing: -0.25px; color: var(--text); }
            .metric-subtext{ color: var(--text-muted); font-size: 0.78rem; }
            .control-card{ background: var(--surface-alt); border-radius: var(--radius); padding: 18px 18px 22px 18px; border: 1px solid var(--border); box-shadow: none; }
            .control-card label{ font-weight: 600; color: var(--text); font-size: 0.88rem; }
            .dash-tabs{ 
    display:flex; 
    flex-wrap:wrap; 
    gap:12px; 
    padding:16px 18px; 
    margin-bottom:8px; 
    background: linear-gradient(145deg, #ffffff 0%, #f6f9fc 48%, #edf3f7 100%); 
    border:1px solid rgba(229,231,235,0.9); 
    border-radius:16px; 
    box-shadow: inset 0 2px 4px rgba(255,255,255,0.85), 0 12px 32px rgba(15,23,42,0.05), 0 4px 12px rgba(15,118,110,0.02); 
    position:relative;
    overflow-x:auto;
    overflow-y:visible;
}
.dash-tabs::before{
    content:"";
    position:absolute;
    inset:0;
    background:linear-gradient(120deg, transparent 0%, rgba(15,118,110,0.015) 50%, transparent 100%);
    border-radius:16px;
    pointer-events:none;
}
.dash-tabs .tab{ 
    position:relative; 
    border:1.5px solid rgba(91,100,117,0.12); 
    background:linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); 
    color:var(--text-muted); 
    padding:13px 18px; 
    border-radius:11px; 
    box-shadow:0 8px 20px rgba(15,23,42,0.04), 0 2px 8px rgba(15,23,42,0.02); 
    transition:all 0.18s cubic-bezier(0.4, 0, 0.2, 1); 
    font-weight:700; 
    font-size:0.88rem;
    letter-spacing:-0.01em;
    cursor:pointer;
    user-select:none;
    min-width:max-content;
}
.dash-tabs .tab::before{
    content:"";
    position:absolute;
    inset:-1px;
    background:linear-gradient(135deg, rgba(255,255,255,0.6), transparent);
    border-radius:11px;
    opacity:0;
    transition:opacity 0.18s ease;
    pointer-events:none;
}
.dash-tabs .tab:hover{ 
    color:var(--text); 
    border-color:rgba(15,118,110,0.4); 
    background:linear-gradient(135deg, #ffffff 0%, #f8fcfb 100%); 
    transform:translateY(-2px) scale(1.01); 
    box-shadow:0 14px 28px rgba(15,23,42,0.08), 0 4px 12px rgba(15,118,110,0.06), inset 0 1px 0 rgba(255,255,255,0.9); 
}
.dash-tabs .tab:hover::before{
    opacity:1;
}
.dash-tabs .tab:active{
    transform:translateY(-1px) scale(0.99);
}
.dash-tabs .tab:focus-visible{ 
    outline:2.5px solid rgba(15,118,110,0.5); 
    outline-offset:3px; 
}
.dash-tabs .tab--selected{ 
    color:var(--accent); 
    border-color:rgba(15,118,110,0.65); 
    background:linear-gradient(130deg, rgba(15,118,110,0.11) 0%, rgba(15,118,110,0.18) 100%); 
    box-shadow:0 16px 36px rgba(15,118,110,0.14), 0 6px 16px rgba(15,118,110,0.08), inset 0 2px 6px rgba(15,118,110,0.08), inset 0 -1px 2px rgba(255,255,255,0.7); 
    transform:translateY(-2px) scale(1.02); 
    font-weight:800;
}
.dash-tabs .tab--selected::before{
    opacity:0.4;
    background:linear-gradient(135deg, rgba(255,255,255,0.8), rgba(15,118,110,0.1));
}
.dash-tabs .tab--selected::after{ 
    content:""; 
    position:absolute; 
    left:14px; 
    right:14px; 
    bottom:9px; 
    height:3.5px; 
    background:linear-gradient(90deg, transparent 0%, var(--accent) 20%, var(--accent) 80%, transparent 100%); 
    border-radius:999px; 
    opacity:0.9; 
    box-shadow:0 2px 6px rgba(15,118,110,0.3);
}
@media (max-width: 768px){
    .dash-tabs{ 
        padding:12px; 
        gap:8px; 
    }
    .dash-tabs .tab{ 
        flex:1 1 auto; 
        text-align:center; 
        padding:11px 14px;
        font-size:0.85rem;
    }
}
@media (max-width: 480px){
    .dash-tabs .tab{
        width:100%;
        text-align:left;
    }
}
            .btn-primary{ background-color: var(--accent); border-color: var(--accent); box-shadow: none; }
            .btn-primary:hover{ background-color: #0b5f57; border-color: #0b5f57; }
            .Select-control, .Select-menu-outer{ border-radius: 10px; border-color: var(--border) !important; box-shadow: none !important; }
            .Select--multi .Select-value{ background: var(--accent-soft) !important; border: 1px solid var(--border) !important; color: var(--text); border-radius: 8px; }
            .dash-table-container table { font-size: 0.90rem; border-collapse: separate; border-spacing: 0 6px; }
            .dash-table-container .dash-spreadsheet-container table th { background: var(--surface-alt) !important; font-weight: 700 !important; color: var(--text); border: none !important; }
            .dash-table-container .dash-spreadsheet-container table td { background: #fff; border-top: 1px solid #eef1f6 !important; border-bottom: 1px solid #eef1f6 !important; }
            .dash-table-container .dash-spreadsheet-container table tr:hover td { background: rgba(15,118,110,0.05); }
            .footer-note{ text-align: center; color: var(--text-muted); font-size: 0.9rem; margin-top: 30px; }
            
            /* Chatbot Animations */
            @keyframes slideInRight {
                from {
                    opacity: 0;
                    transform: translateX(30px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes slideInLeft {
                from {
                    opacity: 0;
                    transform: translateX(-30px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes typing {
                0%, 100% { opacity: 0.3; }
                50% { opacity: 1; }
            }
            
            .user-message {
                animation: slideInRight 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .assistant-message {
                animation: slideInLeft 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .chat-message {
                transition: all 0.3s ease;
            }
            
            .chat-message:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
            }
            
            #chat-messages {
                scroll-behavior: smooth;
            }
            
            #chat-input {
                transition: border-color 0.2s ease, box-shadow 0.2s ease;
            }
            
            #chat-input:focus {
                outline: none;
                border-color: #0f766e !important;
                box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.1) !important;
            }
            
            #chat-send-btn {
                transition: all 0.2s ease;
            }
            
            #chat-send-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(15, 118, 110, 0.3);
            }
            
            #chat-send-btn:active {
                transform: translateY(0);
            }
            
            .typing-indicator {
                display: inline-flex;
                align-items: center;
                gap: 4px;
                padding: 12px 16px;
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e5e7eb;
                max-width: 80px;
            }
            
            .typing-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: #0f766e;
                animation: typing 1.4s infinite;
            }
            
            .typing-dot:nth-child(2) {
                animation-delay: 0.2s;
            }
            
            .typing-dot:nth-child(3) {
                animation-delay: 0.4s;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

# ---------------------
# Data loader
# ---------------------
def load_data(file_patterns=None):
    companies = []
    kpi_definitions = []
    files = []

    base_dir = os.path.join(os.path.dirname(__file__), "datasets")
    if file_patterns is None:
        if os.path.isdir(base_dir):
            file_patterns = [
                os.path.join(base_dir, "quotate", "*.xlsx"),
                os.path.join(base_dir, "non_quotate", "*.xlsx"),
            ]
        else:
            file_patterns = ["QUOTATE*.xlsx", "*NON-QUOTATE*.xlsx"]

    for pattern in file_patterns:
        files.extend(sorted(glob.glob(pattern)))
    if not files:
        fallback_files = [
            os.path.join(base_dir, "quotate", "QUOTATE-KPI-OSS.xlsx"),
            os.path.join(base_dir, "non_quotate", "NON-QUOTATE-KPI-OSS.xlsx"),
            "QUOTATE-KPI-OSS.xlsx",
            "NON-QUOTATE-KPI-OSS.xlsx",
        ]
        files = [f for f in fallback_files if os.path.exists(f)]
    files = list(dict.fromkeys(files))  # dedupe while preserving order

    for file_path in files:
        if not os.path.exists(file_path):
            continue
        try:
            xls = pd.ExcelFile(file_path)
            sheet_names = xls.sheet_names
            source_type = "Quotate" if "NON" not in file_path.upper() else "Non-Quotate"
            for sheet_name in sheet_names:
                df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                headers = df_raw.iloc[1]
                sectors = df_raw.iloc[0]
                year = None
                try:
                    year_cell = df_raw.iloc[0, 1]
                    if pd.notna(year_cell):
                        year = int(year_cell)
                except:
                    year = None
                current_sector = "Unknown"
                col_idx = 3
                while col_idx < df_raw.shape[1]:
                    sec_cell = sectors[col_idx]
                    if pd.notna(sec_cell) and str(sec_cell).strip() != "":
                        current_sector = str(sec_cell).strip()
                    col_name = str(headers[col_idx]).strip()
                    if col_name and col_name.upper() != "OSS" and col_name.lower() != "nan":
                        company_name = col_name
                        oss_col_idx = col_idx + 1
                        company_kpi_values = {}
                        company_total_oss = 0
                        company_missing_count = 0
                        # iterate KPI rows
                        last_valid_cat = "Unknown"
                        for r in range(2, df_raw.shape[0]):
                            cat = df_raw.iloc[r, 0]
                            kpi_name = df_raw.iloc[r, 1]
                            weight = df_raw.iloc[r, 2]
                            if pd.notna(cat) and str(cat).strip().lower() == "totale":
                                break
                            if pd.isna(kpi_name) or str(kpi_name).strip() == "":
                                continue
                            if pd.isna(cat) or str(cat).strip() == "":
                                cat = last_valid_cat
                            else:
                                last_valid_cat = str(cat).strip()
                                cat = last_valid_cat
                            kpi_id = f"{cat}|{kpi_name}"
                            val_cell = df_raw.iloc[r, col_idx]
                            oss_cell = df_raw.iloc[r, oss_col_idx] if oss_col_idx < df_raw.shape[1] else None
                            is_missing = 1 if (pd.notna(val_cell) and str(val_cell).strip() == "1") else 0
                            try:
                                oss_score = float(oss_cell) if pd.notna(oss_cell) else 0
                            except:
                                oss_score = 0
                            company_kpi_values[kpi_id] = {"value": is_missing, "oss": oss_score}
                            company_total_oss += oss_score
                            if is_missing:
                                company_missing_count += 1
                        companies.append({
                            "Company": company_name,
                            "Sector": current_sector,
                            "Type": source_type,
                            "Year": year,
                            "Total_Missing_KPIs": company_missing_count,
                            "Total_OSS_Score": company_total_oss,
                            "kpi_data": company_kpi_values
                        })
                        col_idx += 2
                    else:
                        col_idx += 1
                # build kpi_definitions from first sheet encountered (if not present)
                if not kpi_definitions:
                    last_valid_cat = "Unknown"
                    for r in range(2, df_raw.shape[0]):
                        cat = df_raw.iloc[r, 0]
                        kpi_name = df_raw.iloc[r, 1]
                        weight = df_raw.iloc[r, 2]
                        if pd.notna(cat) and str(cat).strip().lower() == "totale":
                            break
                        if pd.isna(kpi_name) or str(kpi_name).strip() == "":
                            continue
                        if pd.isna(cat) or str(cat).strip() == "":
                            cat = last_valid_cat
                        else:
                            last_valid_cat = str(cat).strip()
                            cat = last_valid_cat
                        kpi_definitions.append({
                            "Category": cat,
                            "KPI": str(kpi_name).strip(),
                            "Weight": float(weight) if pd.notna(weight) else 0,
                            "ID": f"{cat}|{kpi_name}"
                        })
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    df_companies = pd.DataFrame(companies)
    df_kpi_defs = pd.DataFrame(kpi_definitions)
    if not df_companies.empty and not df_kpi_defs.empty:
        total_kpis = len(df_kpi_defs)
        df_companies["Transparency_Percentage"] = (df_companies["Total_Missing_KPIs"] / total_kpis * 100).round(2)
        df_companies["Present_Percentage"] = (100 - df_companies["Transparency_Percentage"]).round(2)
        full_kpi_rows = []
        for _, def_row in df_kpi_defs.iterrows():
            row_item = {"Category": def_row["Category"], "KPI": def_row["KPI"], "Weight": def_row["Weight"], "ID": def_row["ID"]}
            kpi_id = def_row["ID"]
            for _, comp_row in df_companies.iterrows():
                comp_data = comp_row["kpi_data"].get(kpi_id, {"value": 0, "oss": 0})
                row_item[f"{comp_row['Company']}_value"] = comp_data["value"]
                row_item[f"{comp_row['Company']}_oss"] = comp_data["oss"]
            full_kpi_rows.append(row_item)
        df_kpis = pd.DataFrame(full_kpi_rows)
        df_companies = df_companies.drop(columns=["kpi_data"])
        df_companies = df_companies.drop_duplicates(subset=["Company", "Sector", "Type", "Year"], keep="first")
        return df_companies, df_kpis
    return pd.DataFrame(), pd.DataFrame()

companies_df, kpi_df = load_data()

# ---------------------
# Severity logic & helpers
# ---------------------
def get_oss_severity(score):
    if score == 0:
        return "N/A"
    if score <= 31: return "Trasparente"
    if score <= 62: return "Bassa"
    if score <= 93: return "Moderata"
    if score <= 124: return "Grave"
    if score <= 155: return "Critica"
    return "Estrema"

if not companies_df.empty:
    companies_df["Severity"] = companies_df["Total_OSS_Score"].apply(get_oss_severity)
    companies_df = companies_df.sort_values("Total_OSS_Score")

severity_colors = {
    "Trasparente": "#27ae60",
    "Bassa": "#2980b9",
    "Moderata": "#f1c40f",
    "Grave": "#e67e22",
    "Critica": "#e74c3c",
    "Estrema": "#6c3483"
}

def polish_figure(fig, height=600, margin=None):
    base_margin = {"t": 60, "b": 80, "l": 60, "r": 30}
    if margin:
        base_margin.update(margin)
    fig.update_layout(
        height=height,
        margin=base_margin,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#0f172a"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)", zeroline=False)
    return fig

# ---------------------
# Bootstrap helper
# ---------------------
def bootstrap_diff(a, b, iterations=3000):
    if len(a) == 0 or len(b) == 0:
        return None
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    diffs = np.empty(iterations)
    for i in range(iterations):
        sa = np.random.choice(a, size=len(a), replace=True)
        sb = np.random.choice(b, size=len(b), replace=True)
        diffs[i] = sa.mean() - sb.mean()
    ci_low, ci_high = np.percentile(diffs, [2.5, 97.5])
    p_two = 2 * min((diffs >= 0).mean(), (diffs <= 0).mean())
    return {"diff_mean": diffs.mean(), "ci_low": ci_low, "ci_high": ci_high, "p_value": p_two}

# ---------------------
# UI components
# ---------------------
header = dbc.Row([dbc.Col(html.Div([html.H2("The Blind Spot", className="header-title"), html.Div("Gender Equality Transparency Dashboard", className="header-sub")], className="page-header"), md=8)], className="mb-4")

def metric(title, value, sub):
    return dbc.Card(dbc.CardBody([html.Div(title, className="metric-title"), html.Div(value, className="metric-value"), html.Div(sub, className="metric-subtext")]), className="elegant-card")

metrics = dbc.Row([
    dbc.Col(metric("Companies", int(companies_df['Company'].nunique()) if not companies_df.empty else 0, "Unique companies analyzed"), md=3),
    dbc.Col(metric("KPIs", len(kpi_df) if kpi_df is not None else 0, "Tracked indicators"), md=3),
    dbc.Col(metric("Max OSS", "185", "Upper bound of scale"), md=3),
    dbc.Col(metric("Average OSS", f"{companies_df['Total_OSS_Score'].mean():.1f}" if not companies_df.empty else "0", "Across dataset"), md=3)
], className="mb-4")

if not companies_df.empty:
    sector_options = [{"label": s, "value": s} for s in sorted(companies_df["Sector"].unique())]
    severity_options = [{"label": k, "value": k} for k in severity_colors]
    year_options = [{"label": str(y), "value": y} for y in sorted(companies_df["Year"].unique())]
    type_options = [{"label": t, "value": t} for t in sorted(companies_df["Type"].unique())]
else:
    sector_options = []
    severity_options = []
    year_options = []
    type_options = []

download_button = dbc.Card(dbc.CardBody([
    html.Div("Export Report", style={"fontWeight": "700", "marginBottom": "16px"}),
    html.Label("Generate Narrative Report"),
    html.P("Download an AI-generated analysis based on filtered data", style={"fontSize": "0.85rem", "color": "#5b6475", "marginBottom": "12px"}),
    dbc.Button("📄 Generate & Download Report", id="download-report-btn", color="success", className="w-100", style={"marginBottom": "8px"}),
    dcc.Download(id="download-report-file"),
    html.Div(id="report-status", style={"fontSize": "0.85rem", "color": "#0f766e", "marginTop": "8px", "textAlign": "center"})
]), className="control-card", style={"marginTop": "16px"})

download_report_section = html.Div([
    html.Hr(style={"margin": "20px 0", "borderColor": "#e5e7eb"}),
    html.Div("Export Report", style={"fontWeight": "700", "marginBottom": "12px", "color": "#0f766e"}),
    html.P("Generate AI-powered narrative report", style={"fontSize": "0.8rem", "color": "#5b6475", "marginBottom": "10px"}),
    dbc.Button("📄 Generate Report", id="download-report-btn", color="success", className="w-100", style={"marginBottom": "8px", "fontSize": "0.9rem"}),
    dcc.Download(id="download-report-file"),
    dbc.Spinner(
        html.Div(id="report-status", style={"fontSize": "0.8rem", "color": "#0f766e", "marginTop": "8px", "textAlign": "center", "minHeight": "20px"}),
        color="success",
        type="grow",  # Options: "border", "grow"
        size="sm",
        spinner_style={"marginTop": "8px"}
    )
])

controls = dbc.Card(dbc.CardBody([
    html.Div("Refine Results", style={"fontWeight": "700", "marginBottom": "16px"}),
    html.Label("Year"), dcc.Dropdown(id="year-filter", options=year_options, value=[], multi=True), html.Br(),
    html.Label("Type"), dcc.Dropdown(id="type-filter", options=type_options, value=[], multi=True), html.Br(),
    html.Label("Sector"), dcc.Dropdown(id="sector-filter", options=sector_options, value=[], multi=True), html.Br(),
    html.Label("Severity"), dcc.Dropdown(id="severity-filter", options=severity_options, value=[], multi=True), html.Br(),
    html.Label("Company"), dcc.Dropdown(id="company-filter", options=[], value=[], multi=True), html.Br(),
    html.Label("Sort By"),
    dcc.Dropdown(id="sortby-filter", options=[
        {"label": "Severity Ascending", "value": "severity-asc"},
        {"label": "Severity Descending", "value": "severity-desc"},
        {"label": "Company A-Z", "value": "company-az"},
        {"label": "Company Z-A", "value": "company-za"},
    ], value="severity-asc", clearable=False),
    html.Br(),
    dbc.Button("Reset Filters", id="reset-btn", color="primary", className="w-100"),
    html.Div(id="reset-trigger", style={"display": "none"}),
    download_report_section  
]), className="control-card")

tabs = dcc.Tabs(id="main-tabs", value="tab-about", className="dash-tabs", children=[
    dcc.Tab(label="About", value="tab-about"),
    dcc.Tab(label="Overview (OSS)", value="tab-oss"),
    dcc.Tab(label="Quotate Gap", value="tab-gap"),
    dcc.Tab(label="Severity Analysis", value="tab-severity"),
    dcc.Tab(label="Sector Comparison", value="tab-sector"),
    dcc.Tab(label="Trend Analysis", value="tab-trends"),
    dcc.Tab(label="KPI Breakdown", value="tab-kpi-breakdown"),
    dcc.Tab(label="KPI Radar", value="tab-radar"),
    
    dcc.Tab(label="Data Table", value="tab-data"),
    
    dcc.Tab(label="💬 AI Chat", value="tab-chat"),
])
# dcc.Tab(label="Category Impact", value="tab-cat-impact"),

main_display = dbc.Card(dbc.CardBody([tabs, html.Div(id="tab-content", className="mt-3")]), className="elegant-card")

footer = html.Div([html.Div("The Blind Spot — Analysis framework for gender-related reporting transparency."), html.Img(src="/assets/team=logo.png", style={"height": "69px", "marginTop": "10px", "filter": "grayscale(0.2)", "opacity": 0.9}, alt="Ingenium Logo")], className="footer-note")

app.layout = dbc.Container([header, metrics, dbc.Row([dbc.Col(controls, md=3, className="mb-3"), dbc.Col(main_display, md=9)]), footer], fluid=True, className="p-4")

# ---------------------
# Callbacks
# ---------------------
@app.callback(
    Output("company-filter", "options"),
    Input("year-filter", "value"),
    Input("type-filter", "value"),
    Input("sector-filter", "value"),
    Input("severity-filter", "value"),
    Input("reset-trigger", "children")
)
def update_company_list(years, types, sectors, severities, _):
    if companies_df.empty:
        return []
    df = companies_df.copy()
    if years:
        df = df[df["Year"].isin(years)]
    if types:
        df = df[df["Type"].isin(types)]
    if sectors:
        df = df[df["Sector"].isin(sectors)]
    if severities:
        df = df[df["Severity"].isin(severities)]
    return [{"label": c, "value": c} for c in sorted(df["Company"].unique())]

@app.callback(
    Output("tab-content", "children"),
    Input("main-tabs", "value"),
    Input("year-filter", "value"),
    Input("type-filter", "value"),
    Input("sector-filter", "value"),
    Input("company-filter", "value"),
    Input("severity-filter", "value"),
    Input("sortby-filter", "value")
)
def render_tab(tab, years, types, sectors, companies, severities, sortby):
    if companies_df.empty:
        return html.Div("No data loaded. Please ensure Excel files are present.", className="p-3 text-muted")

    df = companies_df.copy()
    if years:
        df = df[df["Year"].isin(years)]
    if types:
        df = df[df["Type"].isin(types)]
    if sectors:
        df = df[df["Sector"].isin(sectors)]
    if companies:
        df = df[df["Company"].isin(companies)]
    if severities:
        df = df[df["Severity"].isin(severities)]

    if df.empty:
        return html.Div("No companies match the selected filters.", style={"color": "#777"})

    # Sorting
    if sortby == "severity-asc":
        df = df.sort_values(["Total_OSS_Score", "Company"], ascending=[True, True])
    elif sortby == "severity-desc":
        df = df.sort_values(["Total_OSS_Score", "Company"], ascending=[False, True])
    elif sortby == "company-az":
        df = df.sort_values("Company", ascending=True)
    elif sortby == "company-za":
        df = df.sort_values("Company", ascending=False)

    px.defaults.template = "plotly_white"

    # TAB 1
    if tab == "tab-oss":
        fig = px.bar(df, x="Company", y="Total_OSS_Score", color="Severity", color_discrete_map=severity_colors,
                     hover_data=["Sector", "Type", "Year"], title="OSS Score Distribution (Lower = More Transparent)", text="Total_OSS_Score")
        fig.update_traces(textposition="outside", marker_line_width=0, marker=dict(opacity=0.92))
        fig.update_layout(xaxis_tickangle=-45)
        fig = polish_figure(fig, height=620, margin={"t": 70, "b": 160})
        return dcc.Graph(figure=fig, config={"displayModeBar": False})

    # TAB 2
    if tab == "tab-severity":
        counts = df["Severity"].value_counts().reset_index()
        counts.columns = ["Severity", "Count"]
        pie = px.pie(counts, names="Severity", values="Count", hole=0.4, color="Severity", color_discrete_map=severity_colors,
                     title="Distribution of Severity Levels")
        pie.update_traces(textinfo="percent+label", pull=[0.03]*len(counts))
        pie = polish_figure(pie, height=560, margin={"t": 60, "b": 40})
        return dcc.Graph(figure=pie, config={"displayModeBar": False})

    # TAB 3
    if tab == "tab-sector":
        sector_order = df.groupby("Sector")["Total_OSS_Score"].median().sort_values().index.tolist()
        if df["Sector"].nunique() > 1:
            box = px.box(df, x="Sector", y="Total_OSS_Score", points="all", color="Severity",
                         color_discrete_map=severity_colors, category_orders={"Sector": sector_order},
                         title="OSS Score Variation by Sector")
            box.update_traces(marker_line_width=0, jitter=0.2)
            box.update_layout(xaxis_tickangle=-45)
            box = polish_figure(box, height=620, margin={"t": 70, "b": 170})
            return dcc.Graph(figure=box, config={"displayModeBar": False})
        else:
            strip = px.strip(df, x="Sector", y="Total_OSS_Score", color="Severity", color_discrete_map=severity_colors,
                             hover_data=["Company"], title="OSS Scores for Selected Sector")
            strip.update_traces(marker_line_width=0, marker=dict(size=10, opacity=0.85))
            strip = polish_figure(strip, height=560, margin={"t": 70, "b": 120})
            return dcc.Graph(figure=strip, config={"displayModeBar": False})

    # TAB 4: 
    if tab == "tab-trends":
        if "Year" not in df.columns:
            return html.Div("No trend data available.", style={"color": "#777", "padding": "20px"})
        companies_with_trends = df.groupby("Company")["Year"].nunique()
        companies_with_trends = companies_with_trends[companies_with_trends > 1].index.tolist()
        if not companies_with_trends:
            return html.Div("No companies with multi-year data available.", style={"color": "#777", "padding": "20px"})
        
        trend_df = df[df["Company"].isin(companies_with_trends)].sort_values(["Company", "Year"])
        
        trend_stats = []
        for company in companies_with_trends:
            comp_data = trend_df[trend_df["Company"] == company].sort_values("Year")
            if len(comp_data) >= 2:
                first_year = comp_data.iloc[0]
                last_year = comp_data.iloc[-1]
                
                if first_year["Total_OSS_Score"] == 0 or last_year["Total_OSS_Score"] == 0:
                    continue
                
                oss_change = last_year["Total_OSS_Score"] - first_year["Total_OSS_Score"]
                years_span = last_year["Year"] - first_year["Year"]
                avg_annual_change = oss_change / years_span if years_span > 0 else 0
                direction = "↓ Improving" if oss_change < 0 else ("↑ Worsening" if oss_change > 0 else "→ Stable")
                
                trend_stats.append({
                    "Company": company,
                    "Start Year": int(first_year["Year"]),
                    "End Year": int(last_year["Year"]),
                    "Start OSS": first_year["Total_OSS_Score"],
                    "End OSS": last_year["Total_OSS_Score"],
                    "Change": oss_change,
                    "Avg Annual Change": avg_annual_change,
                    "Direction": direction,
                    "Start Severity": first_year["Severity"],
                    "End Severity": last_year["Severity"]
                })
        
        trend_stats_df = pd.DataFrame(trend_stats)
        
        improving = len(trend_stats_df[trend_stats_df["Change"] < 0])
        worsening = len(trend_stats_df[trend_stats_df["Change"] > 0])
        stable = len(trend_stats_df[trend_stats_df["Change"] == 0])
        avg_change = trend_stats_df["Change"].mean()
        
        summary_cards = dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div("Companies Improving", className="metric-title"),
                        html.Div(improving, className="metric-value", style={"color": "#27ae60"}),
                        html.Div(f"(OSS decreasing)", className="metric-subtext")
                    ]),
                    className="elegant-card"
                ),
                md=3
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div("Companies Worsening", className="metric-title"),
                        html.Div(worsening, className="metric-value", style={"color": "#e74c3c"}),
                        html.Div(f"(OSS increasing)", className="metric-subtext")
                    ]),
                    className="elegant-card"
                ),
                md=3
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div("Avg Annual Change", className="metric-title"),
                        html.Div(f"{avg_change:+.2f}", className="metric-value", style={"color": "#0f766e"}),
                        html.Div("Points per year", className="metric-subtext")
                    ]),
                    className="elegant-card"
                ),
                md=3
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div("Companies Tracked", className="metric-title"),
                        html.Div(len(trend_stats_df), className="metric-value", style={"color": "#2980b9"}),
                        html.Div("With multi-year data", className="metric-subtext")
                    ]),
                    className="elegant-card"
                ),
                md=3
            ),
        ], className="mb-4")
        
        fig = px.line(
            trend_df, 
            x="Year", 
            y="Total_OSS_Score", 
            color="Company", 
            hover_data={
                "Sector": True,
                "Type": True,
                "Severity": True,
                "Total_Missing_KPIs": True,
                "Present_Percentage": ":.1f"
            },
            title="OSS Score Trends Over Time (Lower = Better Transparency)",
            markers=True,
            custom_data=["Sector", "Type", "Severity"]
        )

        fig.update_traces(
            mode='lines+markers',
            marker=dict(
                size=12,
                opacity=0.9,
                line=dict(width=2, color='white')
            ),
            line=dict(width=3),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                          'Year: %{x}<br>' +
                          'OSS Score: %{y:.1f}<br>' +
                          'Sector: %{customdata[0]}<br>' +
                          'Type: %{customdata[1]}<br>' +
                          'Severity: %{customdata[2]}<extra></extra>'
        )
        
        fig.update_layout(
            hovermode="x unified",
            xaxis=dict(
                type="category",
                title="Year",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.05)'
            ),
            yaxis=dict(
                title="OSS Score (Lower = More Transparent)",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.05)',
                zeroline=False
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color="#0b1220", size=11),
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1
            ),
            margin={"t": 70, "b": 100, "l": 70, "r": 40},
            height=680
        )
        
        table_df = trend_stats_df[["Company", "Start Year", "End Year", "Start OSS", "End OSS", "Change", "Avg Annual Change", "Direction"]].copy()
        
        table_df["Start OSS"] = table_df["Start OSS"].round(2)
        table_df["End OSS"] = table_df["End OSS"].round(2)
        table_df["Change"] = table_df["Change"].round(2)
        table_df["Avg Annual Change"] = table_df["Avg Annual Change"].round(2)
        
        table_df = table_df.sort_values("Change")

        if trend_stats_df.empty:
            return html.Div("No companies with valid trend data.", style={"color": "#777", "padding": "20px"})

        trend_table = dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in table_df.columns],
            data=table_df.to_dict("records"),
            style_table={"overflowX": "auto", "marginTop": "20px"},
            style_cell={
                "padding": "12px",
                "textAlign": "center",
                "border": "none",
                "fontSize": "0.9rem",
                "fontWeight": "500"
            },
            style_header={
                "fontWeight": "700",
                "backgroundColor": "#eef1f8",
                "border": "none",
                "color": "#0f766e",
                "textAlign": "center"
            },
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "rgba(15,118,110,0.02)"
                },
                {
                    "if": {"column_id": "Change", "filter_query": "{Change} < 0"},
                    "backgroundColor": "rgba(39, 174, 96, 0.08)",
                    "color": "#27ae60",
                    "fontWeight": "600"
                },
                {
                    "if": {"column_id": "Change", "filter_query": "{Change} > 0"},
                    "backgroundColor": "rgba(231, 76, 60, 0.08)",
                    "color": "#e74c3c",
                    "fontWeight": "600"
                }
            ]
        )
        
        interval_pairs = [(2021, 2022), (2022, 2023), (2021, 2023)]
        interval_summaries = []
        for start_year, end_year in interval_pairs:
            label = f"{start_year} - {end_year}"
            records = []
            for company in trend_df["Company"].unique():
                comp_slice = trend_df[trend_df["Company"] == company]
                start_row = comp_slice[comp_slice["Year"] == start_year]
                end_row = comp_slice[comp_slice["Year"] == end_year]
                if start_row.empty or end_row.empty:
                    continue
                start_score = start_row.iloc[-1]["Total_OSS_Score"]
                end_score = end_row.iloc[-1]["Total_OSS_Score"]
                if start_score == 0 or end_score == 0:
                    continue
                delta = end_score - start_score
                records.append({
                    "Company": company,
                    "Change": delta,
                    "StartSeverity": start_row.iloc[-1]["Severity"],
                    "EndSeverity": end_row.iloc[-1]["Severity"]
                })
            if not records:
                interval_summaries.append({"label": label, "improve": None, "worsen": None})
                continue
            records = sorted(records, key=lambda x: x["Change"])
            best = records[0]
            worst = records[-1]
            interval_summaries.append({
                "label": label,
                "improve": best if best["Change"] < 0 else None,
                "worsen": worst if worst["Change"] > 0 else None
            })

        interval_items = []
        for summary in interval_summaries:
            improve = summary["improve"]
            worsen = summary["worsen"]
            improve_text = f"{improve['Company']} ({improve['Change']:+.1f}, {improve['StartSeverity']} -> {improve['EndSeverity']})" if improve else "N/A"
            worsen_text = f"{worsen['Company']} ({worsen['Change']:+.1f}, {worsen['StartSeverity']} -> {worsen['EndSeverity']})" if worsen else "N/A"
            interval_items.append(html.Li([
                html.Strong(f"{summary['label']}: "),
                f"Improving: {improve_text} | Worsening: {worsen_text}"
            ], style={"marginBottom": "6px"}))

        most_improved = trend_stats_df.loc[trend_stats_df["Change"].idxmin()]
        most_declined = trend_stats_df.loc[trend_stats_df["Change"].idxmax()]

        insights = dbc.Card(
            dbc.CardBody([
                html.H6("Key Insights", style={"fontWeight": "700", "marginBottom": "12px", "color": "#0f766e"}),
                dbc.Row([
                    dbc.Col([html.P("🟢 Most Improved", style={"fontWeight": "600", "marginBottom": "4px", "color": "#27ae60"}),
                              html.P(f"{most_improved['Company']}: {most_improved['Change']:+.1f} points", style={"marginBottom": "2px"}),
                              html.P(f"From {most_improved['Start Severity']} → {most_improved['End Severity']}", style={"fontSize": "0.85rem", "color": "#5b6475"})], md=6),
                    dbc.Col([html.P("🔴 Most Declined", style={"fontWeight": "600", "marginBottom": "4px", "color": "#e74c3c"}),
                              html.P(f"{most_declined['Company']}: {most_declined['Change']:+.1f} points", style={"marginBottom": "2px"}),
                              html.P(f"From {most_declined['Start Severity']} → {most_declined['End Severity']}", style={"fontSize": "0.85rem", "color": "#5b6475"})], md=6),
                ]),
                html.Hr(style={"margin": "12px 0", "borderColor": "#e5e7eb"}),
                html.P("Interval snapshots", style={"fontWeight": "700", "marginBottom": "6px"}),
                html.Ul(interval_items, style={"paddingLeft": "18px", "color": "#3a3f4b", "fontSize": "0.9rem"}),
                html.Hr(style={"margin": "12px 0", "borderColor": "#e5e7eb"}),
                html.P(
                    "Negative change = improving transparency. Positive change = decreasing transparency. "
                    "The average annual change shows the typical rate of improvement or decline per year.",
                    style={"fontSize": "0.85rem", "color": "#5b6475", "fontStyle": "italic", "marginBottom": 0}
                )
            ]),
            className="elegant-card"
        )
        
        return html.Div([
            summary_cards,
            html.Hr(style={"margin": "20px 0", "borderColor": "#e5e7eb"}),
            dcc.Graph(figure=fig, config={"displayModeBar": True}),
            html.Hr(style={"margin": "30px 0", "borderColor": "#e5e7eb"}),
            html.H5("Trend Summary by Company", style={"fontWeight": "700", "marginBottom": "12px"}),
            trend_table,
            html.Hr(style={"margin": "30px 0", "borderColor": "#e5e7eb"}),
            insights
        ])

    # TAB 5: 
    if tab == "tab-kpi-breakdown":
        if kpi_df.empty or df.empty:
            return html.Div("No KPI data available.", style={"color": "#777", "padding": "20px"})
        labels = ["All KPIs"]; parents = [""]; values = [1]; colors = [0]
        categories = kpi_df["Category"].unique()
        category_missing_counts = {}; category_total_possible = {}; all_missing_total = 0; all_total = 0
        for cat in categories:
            category_missing_counts[cat] = 0; category_total_possible[cat] = 0
            labels.append(cat); parents.append("All KPIs"); values.append(1); colors.append(0)
        for _, kpi_row in kpi_df.iterrows():
            kpi_name = kpi_row["KPI"]; category = kpi_row["Category"]
            companies_missing = 0
            for _, company_row in df.iterrows():
                company_name = company_row["Company"]; value_col = f"{company_name}_value"
                if value_col in kpi_row.index:
                    if kpi_row[value_col] == 1:
                        companies_missing += 1
            missing_rate = (companies_missing / len(df) * 100) if len(df) > 0 else 0
            labels.append(f"{kpi_name}<br>({missing_rate:.2f}%)"); parents.append(category); values.append(len(df)); colors.append(missing_rate)
            category_missing_counts[category] += companies_missing
            category_total_possible[category] += len(df)
            all_missing_total += companies_missing; all_total += len(df)
        for i, label in enumerate(labels[1:], start=1):
            if label in category_missing_counts:
                category_val = category_missing_counts[label]; category_tot = category_total_possible[label]
                category_pct = (category_val / category_tot * 100) if category_tot > 0 else 0
                colors[i] = category_pct
        root_pct = (all_missing_total / all_total * 100) if all_total > 0 else 0
        colors[0] = root_pct
        sunburst = go.Figure(go.Sunburst(labels=labels, parents=parents, values=values, marker=dict(colors=colors, colorscale="RdYlGn_r", cmid=50, colorbar=dict(title="Missing %"), line=dict(width=0.5, color="white")), insidetextorientation='radial', hovertemplate="<b>%{label}</b><br>Missing Rate: %{color:.2f}%<extra></extra>"))
        sunburst.update_layout(title="KPI Category Breakdown — Missing Rates Across Selected Companies", height=700)
        sunburst = polish_figure(sunburst, height=700, margin={"t": 80, "b": 40})
        return dcc.Graph(figure=sunburst, config={"displayModeBar": True})

    # TAB 6: 
    if tab == "tab-radar":
        if kpi_df.empty:
            return html.Div("No KPI data available.", style={"color": "#777"})
        
        kpi_data = []
        for _, kpi_row in kpi_df.iterrows():
            kpi_name = kpi_row["KPI"]
            category = kpi_row["Category"]
            weight = kpi_row["Weight"]
            companies_missing = 0
            total_points = 0
            for _, company_row in df.iterrows():
                company_name = company_row["Company"]
                value_col = f"{company_name}_value"
                oss_col = f"{company_name}_oss"
                if value_col in kpi_row.index and oss_col in kpi_row.index:
                    if kpi_row[value_col] == 1:
                        companies_missing += 1
                        total_points += kpi_row[oss_col]
            if companies_missing > 0:
                missing_pct = (companies_missing / len(df) * 100) if len(df) > 0 else 0
                kpi_data.append({
                    'kpi': kpi_name,
                    'category': category,
                    'missing_count': companies_missing,
                    'missing_pct': missing_pct,
                    'total_points': total_points,
                    'weight': weight
                })
        
        if not kpi_data:
            return html.Div("No missing KPIs found in the selected companies.", style={"color": "#777", "padding": "20px"})
        
        kpi_data_sorted = sorted(kpi_data, key=lambda x: x['missing_count'], reverse=True)[:20]
        
        total_unique_missing_kpis = len(kpi_data)
        avg_missing_pct = np.mean([item['missing_pct'] for item in kpi_data])
        max_missing_count = kpi_data_sorted[0]['missing_count'] if kpi_data_sorted else 0
        total_oss_impact = sum([item['total_points'] for item in kpi_data_sorted])
        
        summary_cards = dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div("Total Missing KPIs", className="metric-title"),
                        html.Div(total_unique_missing_kpis, className="metric-value"),
                        html.Div(f"Across {len(df)} entries", className="metric-subtext")
                    ]),
                    className="elegant-card"
                ),
                md=3
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div("Avg Missing Rate", className="metric-title"),
                        html.Div(f"{avg_missing_pct:.1f}%", className="metric-value"),
                        html.Div("Average across all KPIs", className="metric-subtext")
                    ]),
                    className="elegant-card"
                ),
                md=3
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div("Most Missing", className="metric-title"),
                        html.Div(f"{max_missing_count}", className="metric-value"),
                        html.Div("Max missing count (top KPI)", className="metric-subtext")
                    ]),
                    className="elegant-card"
                ),
                md=3
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div("OSS Impact (Top 20)", className="metric-title"),
                        html.Div(f"{total_oss_impact:.0f}", className="metric-value"),
                        html.Div("Total severity points", className="metric-subtext")
                    ]),
                    className="elegant-card"
                ),
                md=3
            ),
        ], className="mb-4")
        
        kpi_labels = [f"{item['kpi'][:30]}" for item in kpi_data_sorted]  
        kpi_labels_full = [item['kpi'] for item in kpi_data_sorted]
        missing_counts = [item['missing_count'] for item in kpi_data_sorted]
        missing_pcts = [item['missing_pct'] for item in kpi_data_sorted]
        total_oss_points = [item['total_points'] for item in kpi_data_sorted]
        categories = [item['category'] for item in kpi_data_sorted]
        
        category_color_map = {
            cat: f"hsl({i*30}, 70%, 50%)" 
            for i, cat in enumerate(sorted(set(categories)))
        }
        bar_colors = [category_color_map[cat] for cat in categories]
        
        bar_df_vis = pd.DataFrame({
            'KPI': kpi_labels,
            'Missing Count': missing_counts,
            'Missing %': missing_pcts,
            'OSS Points': total_oss_points,
            'Category': categories,
            'Full Name': kpi_labels_full
        })
        
        bar_fig = px.bar(
            bar_df_vis,
            x='Missing Count',
            y='KPI',
            orientation='h',
            color='Category',
            hover_data={
                'Missing %': ':.1f',
                'OSS Points': ':.0f',
                'Full Name': True,
                'Category': True,
                'KPI': False
            },
            title="Top 20 Most Missing KPIs by Frequency",
            labels={'Missing Count': 'Number of Entries Missing', 'KPI': 'KPI Name'},
            text='Missing Count'
        )
        
        bar_fig.update_traces(
            textposition='outside',
            hovertemplate='<b>%{customdata[3]}</b>' +
                          '<br>Missing in: %{x} entries' +
                          '<br>Missing Rate: %{customdata[0]:.1f}%' +
                          '<br>OSS Impact: %{customdata[1]:.0f}' +
                          '<br>Category: %{customdata[2]}<extra></extra>',
            marker=dict(line=dict(width=0.5, color='white'))
        )
        
        bar_fig.update_layout(
            height=650,
            xaxis_title='Number of Company-Year Entries Missing',
            yaxis_title='',
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1
            ),
            hovermode='closest',
            margin={"t": 60, "b": 80, "l": 200, "r": 40}
        )
        
        bar_fig = polish_figure(bar_fig, height=650, margin={"t": 60, "b": 80, "l": 200, "r": 200})
        
        radar_fig = go.Figure()
        radar_fig.add_trace(go.Scatterpolar(
            r=missing_counts,
            theta=kpi_labels,
            fill='toself',
            name='Missing Count',
            line=dict(color='#0f766e', width=2.5),
            fillcolor='rgba(15, 118, 110, 0.25)',
            hovertemplate='<b>%{theta}</b>' +
                          '<br>Missing: %{r} entries' +
                          '<br>Rate: %{customdata[0]:.1f}%' +
                          '<br>OSS Points: %{customdata[1]:.0f}<extra></extra>',
            customdata=np.column_stack((missing_pcts, total_oss_points)),
            marker=dict(size=8, color='#e74c3c')
        ))
        
        radar_fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(missing_counts) * 1.2] if missing_counts else [0, 10],
                    showticklabels=True,
                    ticks='outside',
                    gridcolor='rgba(0,0,0,0.1)',
                    tickfont=dict(size=10)
                ),
                angularaxis=dict(
                    rotation=90,
                    direction='clockwise',
                    gridcolor='rgba(0,0,0,0.08)',
                    tickfont=dict(size=10)
                ),
                bgcolor='rgba(240,245,245,0.3)'
            ),
            showlegend=False,
            title=dict(
                text="Radar View: Distribution of Missing KPIs",
                font=dict(size=16, family="Inter", color="#0b1220")
            ),
            height=700,
            font=dict(size=11, family="Inter", color="#0b1220"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin={"t": 80, "b": 40, "l": 40, "r": 40}
        )
        
        rate_df = pd.DataFrame({
            'KPI': kpi_labels_full[:10], 
            'Missing Count': missing_counts[:10],
            'Missing Rate (%)': [f"{p:.1f}" for p in missing_pcts[:10]],
            'Category': categories[:10],
            'OSS Impact': [f"{p:.0f}" for p in total_oss_points[:10]]
        })
        
        rate_table = dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in rate_df.columns],
            data=rate_df.to_dict("records"),
            style_table={"overflowX": "auto", "marginTop": "20px"},
            style_cell={"padding": "10px", "textAlign": "left", "border": "none", "fontSize": "0.9rem"},
            style_header={"fontWeight": "700", "backgroundColor": "#eef1f8", "border": "none", "color": "#0f766e"},
            style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "rgba(15,118,110,0.03)"}]
        )
        
        explanation = dbc.Card(
            dbc.CardBody([
                html.H6("How to Read This Tab", style={"fontWeight": "700", "marginBottom": "12px"}),
                html.Ul([
                    html.Li([html.Strong("Missing Count:"), " Number of company-year entries missing this KPI"]),
                    html.Li([html.Strong("Missing Rate (%):"), " Percentage of selected entries missing this KPI"]),
                    html.Li([html.Strong("OSS Impact:"), " Total severity points from missing this KPI across entries"]),
                    html.Li([html.Strong("Top 20:"), " Sorted by frequency—these are the most commonly missing KPIs"])
                ], style={"color": "#5b6475", "fontSize": "0.9rem"}),
                html.P("Use these insights to identify KPIs that most companies struggle to report, indicating potential areas for targeted improvement or industry-wide guidance.", 
                       style={"marginTop": "12px", "color": "#5b6475", "fontSize": "0.85rem", "fontStyle": "italic"})
            ]),
            className="elegant-card"
        )
        
        return html.Div([
            summary_cards,
            html.Hr(style={"margin": "20px 0", "borderColor": "#e5e7eb"}),
            dcc.Graph(figure=bar_fig, config={"displayModeBar": True}),
            html.Hr(style={"margin": "30px 0", "borderColor": "#e5e7eb"}),
            rate_table,
            html.Hr(style={"margin": "30px 0", "borderColor": "#e5e7eb"}),
            dcc.Graph(figure=radar_fig, config={"displayModeBar": True}),
            html.Hr(style={"margin": "30px 0", "borderColor": "#e5e7eb"}),
            explanation
        ])

    # TAB 7: 
    if tab == "tab-data":
        sub = df[["Company", "Sector", "Type", "Year", "Total_OSS_Score", "Severity", "Total_Missing_KPIs", "Transparency_Percentage", "Present_Percentage"]].copy()
        sub = sub.fillna("N/A")
        numeric_cols = ["Total_OSS_Score", "Total_Missing_KPIs", "Transparency_Percentage", "Present_Percentage"]
        for col in numeric_cols:
            sub[col] = sub[col].apply(lambda x: "N/A" if x == 0 else x)
        table = dash_table.DataTable(columns=[{"name": c, "id": c} for c in sub.columns], data=sub.to_dict("records"), page_size=12, sort_action="native", style_table={"overflowX": "auto"}, style_cell={"padding": "12px", "textAlign": "left", "border": "none"}, style_header={"fontWeight": "800", "backgroundColor": "#eef1f8", "border": "none"}, style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "rgba(124,93,250,0.03)"}])
        return table

    # TAB 8: 
    if tab == "tab-about":
        return dbc.Card(dbc.CardBody([
            html.Div([
                html.H3("The Blind Spot", style={"fontWeight": "800", "color": "#0b1220"}),
                html.H5("When Missing Data Speaks Louder than Numbers", style={"color": "#5b6475", "marginBottom": "24px"}),
                
                html.Div([
                    html.P([
                        "While many analyze the data present in Non-Financial Declarations (DNFs)—such as pay gaps or % of women in STEM—",
                        html.Strong("we analyze what is missing."),
                        " Our goal is to visualize the 'information gap,' transforming the absence of data into an indicator of transparency and real commitment."
                    ]),
                    html.Blockquote(
                        "\"What isn't measured, isn't managed. What isn't communicated, often doesn't exist. We make the invisible visible.\"",
                        style={"borderLeft": "4px solid #0f766e", "paddingLeft": "15px", "margin": "20px 0", "fontStyle": "italic", "color": "#444"}
                    )
                ], style={"marginBottom": "35px"}),

                html.Hr(style={"borderColor": "#e5e7eb"}),

                html.H5("Methodology: The OSS System", style={"fontWeight": "700", "color": "#0f766e", "marginTop": "25px"}),
                html.P("The analysis is based on a checklist of KPIs derived from European directives and ESG standards. We utilize the Omission Severity Score (OSS) to quantify opacity."),
                
                dbc.Row([
                    dbc.Col([
                        html.Div("1. Binary Collection", style={"fontWeight": "700"}),
                        html.P("Is the KPI present? Yes = 0 points, No = 1 point.", style={"fontSize": "0.9rem", "color": "#5b6475"})
                    ], md=4),
                    dbc.Col([
                        html.Div("2. Weighted Severity", style={"fontWeight": "700"}),
                        html.P("Not all omissions are equal. Missing a 'Gender Pay Gap' metric (Weight 3) is more severe than missing a generic training metric (Weight 1).", style={"fontSize": "0.9rem", "color": "#5b6475"})
                    ], md=4),
                    dbc.Col([
                        html.Div("3. Calculation", style={"fontWeight": "700"}),
                        html.P("OSS = Σ (Missing KPI × Weight). Max Score = 185.", style={"fontSize": "0.9rem", "color": "#5b6475"})
                    ], md=4),
                ], className="mb-4"),

                html.H6("The Severity Scale", style={"fontWeight": "700", "marginTop": "20px"}),
                html.Div([
                    # Header
                    dbc.Row([
                        dbc.Col("OSS Score", width=2, style={"fontWeight": "700", "color": "#0f766e"}),
                        dbc.Col("Level", width=3, style={"fontWeight": "700", "color": "#0f766e"}),
                        dbc.Col("Interpretation", width=7, style={"fontWeight": "700", "color": "#0f766e"}),
                    ], className="mb-2", style={"borderBottom": "1px solid #e5e7eb", "paddingBottom": "8px"}),
                    # Rows
                    dbc.Row([
                        dbc.Col("0 - 31", width=2, style={"fontWeight": "600"}),
                        dbc.Col(html.Span("Trasparente", style={"backgroundColor": "#27ae60", "color": "white", "padding": "2px 8px", "borderRadius": "12px", "fontSize": "0.85rem"}), width=3),
                        dbc.Col("Minimal omissions. The company communicates almost everything.", width=7),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col("32 - 62", width=2, style={"fontWeight": "600"}),
                        dbc.Col(html.Span("Bassa", style={"backgroundColor": "#2980b9", "color": "white", "padding": "2px 8px", "borderRadius": "12px", "fontSize": "0.85rem"}), width=3),
                        dbc.Col("Low omission level. Few gaps.", width=7),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col("63 - 93", width=2, style={"fontWeight": "600"}),
                        dbc.Col(html.Span("Moderata", style={"backgroundColor": "#f1c40f", "color": "black", "padding": "2px 8px", "borderRadius": "12px", "fontSize": "0.85rem"}), width=3),
                        dbc.Col("Moderate. Several important KPIs are missing.", width=7),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col("94 - 124", width=2, style={"fontWeight": "600"}),
                        dbc.Col(html.Span("Grave", style={"backgroundColor": "#e67e22", "color": "white", "padding": "2px 8px", "borderRadius": "12px", "fontSize": "0.85rem"}), width=3),
                        dbc.Col("Severe. Significant omissions including essential KPIs.", width=7),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col("125 - 155", width=2, style={"fontWeight": "600"}),
                        dbc.Col(html.Span("Critica", style={"backgroundColor": "#e74c3c", "color": "white", "padding": "2px 8px", "borderRadius": "12px", "fontSize": "0.85rem"}), width=3),
                        dbc.Col("Critical. Fundamental and structural KPIs are missing.", width=7),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col("156 - 185", width=2, style={"fontWeight": "600"}),
                        dbc.Col(html.Span("Estrema", style={"backgroundColor": "#6c3483", "color": "white", "padding": "2px 8px", "borderRadius": "12px", "fontSize": "0.85rem"}), width=3),
                        dbc.Col("Extreme. The company omites almost all critical areas.", width=7),
                    ], className="mb-2"),
                ], style={"backgroundColor": "#f8fafc", "padding": "20px", "borderRadius": "12px"}),

                html.Div([
                    html.H6("Key Areas Monitored", style={"fontWeight": "700", "marginTop": "25px"}),
                    html.Ul([
                        html.Li("Board & Governance (e.g., % women in committees)"),
                        html.Li("Management (e.g., % women in top management)"),
                        html.Li("Pay Equity (e.g., Adjusted/Unadjusted Pay Gap, Bonus Gap)"),
                        html.Li("STEM & Strategy (e.g., % women in R&D, ICT)"),
                        html.Li("Work-Life Balance & Welfare (e.g., Parental leave beyond legal minimum)"),
                        html.Li("Inclusion Culture (e.g., Anti-bias training, Diversity Managers)")
                    ], style={"columns": "2", "color": "#5b6475"})
                ])
            ])
        ]), className="elegant-card")
    
    # TAB 9: 
    if tab == "tab-cat-impact":
        if kpi_df.empty or df.empty:
            return html.Div("No KPI data available.", style={"color": "#777", "padding": "20px"})

        categories = sorted(kpi_df["Category"].unique())
        records = []
        total_possible = 0.0
        total_missing_weight = 0.0

        for cat in categories:
            kpis_cat = kpi_df[kpi_df["Category"] == cat]
            missing_weight_sum = 0.0
            possible_weight_sum = 0.0
            for _, kpi_row in kpis_cat.iterrows():
                weight = kpi_row.get("Weight", 0) or 0
                possible_weight_sum += weight * len(df)
                missing_count = 0
                for _, company_row in df.iterrows():
                    val_col = f"{company_row['Company']}_value"
                    if val_col in kpi_row.index and kpi_row[val_col] == 1:
                        missing_count += 1
                missing_weight_sum += weight * missing_count
            if possible_weight_sum > 0:
                rate_pct = (missing_weight_sum / possible_weight_sum * 100) if possible_weight_sum else 0
                records.append({
                    "category": cat,
                    "missing_weight": missing_weight_sum,
                    "possible_weight": possible_weight_sum,
                    "rate_pct": rate_pct
                })
                total_possible += possible_weight_sum
                total_missing_weight += missing_weight_sum

        if not records:
            return html.Div("No weighted data to display.", style={"color": "#777", "padding": "20px"})

        cat_df = pd.DataFrame(records)
        
        overall_rate = (total_missing_weight / total_possible * 100) if total_possible > 0 else 0
        
        top_row = cat_df.sort_values("rate_pct", ascending=True).iloc[0]
        
        cards = dbc.Row([
            dbc.Col(card("Top gap category", f"{top_row['category']} ({top_row['rate_pct']:.1f}%)"), md=3),
            dbc.Col(card("Categories covered", f"{len(cat_df)}"), md=3),
        ], className="mb-3")

        labels = ["All Categories"]
        parents = [""]
        values = [max(total_missing_weight, 0.0001)]
        colors = [overall_rate]
        customdata = [[total_missing_weight, total_possible, overall_rate, 100.0]]
        for _, rec in cat_df.iterrows():
            labels.append(rec["category"])
            parents.append("All Categories")
            values.append(rec["missing_weight"] if rec["missing_weight"] > 0 else 0.0001)
            colors.append(rec["rate_pct"])
            customdata.append([rec["missing_weight"], rec["possible_weight"], rec["rate_pct"], rec["share_of_missing"]])

        treemap = go.Figure(go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(colors=colors, colorscale="Reds", colorbar=dict(title="Weighted Missing %"), line=dict(width=0.5, color="white")),
            customdata=customdata,
            hovertemplate="<b>%{label}</b><br>Weighted missing: %{customdata[0]:.2f}"
                          "<br>Possible weight: %{customdata[1]:.2f}"
                          "<br>Weighted missing rate: %{customdata[2]:.2f}%"
                          "<br>Share of total missing: %{customdata[3]:.1f}%<extra></extra>"
        ))
        treemap.update_layout(title="Weighted Category Impact — Contribution to OSS via KPI Weights", height=640)
        treemap = polish_figure(treemap, height=640, margin={"t": 80, "b": 40})

        bar_df = cat_df.sort_values("rate_pct", ascending=True)
        bar = px.bar(
            bar_df,
            x="rate_pct",
            y="category",
            orientation="h",
            color="share_of_missing",
            color_continuous_scale="Reds",
            labels={"rate_pct": "Weighted missing %", "category": "Category", "share_of_missing": "Share of total missing %"},
            hover_data={
                "missing_weight": ":.2f",
                "possible_weight": ":.2f",
                "share_of_missing": ":.1f",
                "rate_pct": ":.1f",
                "category": False
            },
            title="Weighted missing rate by category"
        )
        bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        bar = polish_figure(bar, height=520, margin={"t": 70, "b": 80, "l": 90, "r": 40})

        explainer = html.Div(
            "Weights come from the KPI checklist. Bars rank categories by weighted omission rate; color shows share of total missing weight.",
            style={"marginTop": "12px", "color": "#444"}
        )

        return html.Div([
            cards,
            dcc.Graph(figure=bar, config={"displayModeBar": False}),
            html.Hr(style={"margin": "16px 0"}),
            dcc.Graph(figure=treemap, config={"displayModeBar": True}),
            explainer
        ])

    # TAB 10:
    if tab == "tab-gap":
        if "Type" not in df.columns:
            return html.Div("No data available for gap analysis.", style={"color": "#777", "padding": "20px"})
        q_df = df[df["Type"].str.lower().str.contains("quotate", na=False)]
        n_df = df[df["Type"].str.lower().str.contains("non-quotate", na=False)]
        if q_df.empty or n_df.empty:
            return html.Div("Need both Quotate and Non-Quotate groups to compare.", style={"color": "#777", "padding": "20px"})
        oss_q = q_df["Total_OSS_Score"].dropna()
        oss_n = n_df["Total_OSS_Score"].dropna()
        present_q = q_df["Present_Percentage"].dropna()
        present_n = n_df["Present_Percentage"].dropna()
        oss_gap = bootstrap_diff(oss_q.values, oss_n.values) if len(oss_q) and len(oss_n) else None
        present_gap = bootstrap_diff(present_q.values, present_n.values) if len(present_q) and len(present_n) else None

        def card(title, body):
            return dbc.Card(dbc.CardBody([html.Div(title, className="metric-title"), html.Div(body, className="metric-value")]), className="elegant-card")

        cards = dbc.Row([
            dbc.Col(card("Mean OSS (Quotate)", f"{oss_q.mean():.2f}"), md=3),
            dbc.Col(card("Mean OSS (Non-Quotate)", f"{oss_n.mean():.2f}"), md=3),
            dbc.Col(card("Mean Present% (Quotate)", f"{present_q.mean():.2f}%"), md=3),
            dbc.Col(card("Mean Present% (Non-Quotate)", f"{present_n.mean():.2f}%"), md=3),
        ], className="mb-3")

        summary = []
        if oss_gap:
            summary.append(f"OSS Δ (Quotate - Non): {oss_gap['diff_mean']:.2f} [95% CI {oss_gap['ci_low']:.2f}, {oss_gap['ci_high']:.2f}], p ≈ {oss_gap['p_value']:.3f}")
        if present_gap:
            summary.append(f"Present% Δ (Quotate - Non): {present_gap['diff_mean']:.2f} [95% CI {present_gap['ci_low']:.2f}, {present_gap['ci_high']:.2f}], p ≈ {present_gap['p_value']:.3f}")
        gap_text = html.Ul([html.Li(s) for s in summary], style={"color": "#0f172a", "fontSize": "0.95rem"})

        box = px.box(df, x="Type", y="Total_OSS_Score", color="Type", points="all", title="OSS Score Distribution — Quotate vs Non-Quotate", hover_data=["Company", "Sector", "Year", "Severity"])
        box.update_traces(marker_line_width=0, jitter=0.2)
        box = polish_figure(box, height=600, margin={"t": 70, "b": 120})
        return html.Div([cards, gap_text, dcc.Graph(figure=box, config={"displayModeBar": False})])

    # TAB CHAT:
    if tab == "tab-chat":
        return chatbot_container

    return html.Div("Tab not implemented.", style={"color": "#777"})

# ---------------------
# Flask route
# ---------------------
@app.server.route('/download_pdf/<pdf_id>')
def download_pdf(pdf_id):

    if pdf_id in pdf_storage:
        pdf_bytes = pdf_storage[pdf_id]
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"blind_spot_report_{timestamp}.pdf"
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    return "PDF not found", 404

pdf_storage = {}

@app.callback(
    Output("download-report-file", "data"),
    Output("report-status", "children"),
    Input("download-report-btn", "n_clicks"),
    Input("year-filter", "value"),
    Input("type-filter", "value"),
    Input("sector-filter", "value"),
    Input("company-filter", "value"),
    Input("severity-filter", "value"),
    prevent_initial_call=True
)
def generate_and_download_report(n_clicks, years, types, sectors, companies, severities):
    if n_clicks is None or n_clicks == 0:
        return None, ""
    
    try:
        df = companies_df.copy()
        if years:
            df = df[df["Year"].isin(years)]
        if types:
            df = df[df["Type"].isin(types)]
        if sectors:
            df = df[df["Sector"].isin(sectors)]
        if companies:
            df = df[df["Company"].isin(companies)]
        if severities:
            df = df[df["Severity"].isin(severities)]
        
        if df.empty:
            return None, "❌ No data selected"
        
        rag = BlindSpotRAG()
        
        filters_info = {}
        if years:
            filters_info['years'] = years
        if types:
            filters_info['types'] = types
        if sectors:
            filters_info['sectors'] = sectors
        if severities:
            filters_info['severities'] = severities
        
        report_content = rag.generate_report(df, kpi_df=kpi_df, filters=filters_info)
        
        pdf_bytes = rag.export_report_to_pdf(report_content)
        
        pdf_id = str(uuid.uuid4())
        pdf_storage[pdf_id] = pdf_bytes
        
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"blind_spot_report_{timestamp}.pdf"
        
        pdf_base64 = base64.b64encode(pdf_bytes).decode()
        
        return dict(
            content=pdf_base64,
            filename=filename,
            base64=True,
            type="application/pdf"
        ), f"✅ Report ready ({len(df)} cos.)"
    
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return None, f"❌ Error: {str(e)[:50]}"

# Reset callback
@app.callback(
    Output("year-filter", "value"),
    Output("type-filter", "value"),
    Output("sector-filter", "value"),
    Output("severity-filter", "value"),
    Output("company-filter", "value"),
    Output("reset-trigger", "children"),
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_filters(n):
    return ([], [], [], [], [], f"reset-{n}")

# ---------------------
# Chatbot callback
# ---------------------
@app.callback(
    Output("chat-messages", "children"),
    Output("conversation-store", "data"),
    Output("chat-input", "value"),
    Input("chat-send-btn", "n_clicks"),
    Input("chat-input", "n_submit"),
    State("chat-input", "value"),
    State("conversation-store", "data"),
    State("year-filter", "value"),
    State("type-filter", "value"),
    State("sector-filter", "value"),
    State("company-filter", "value"),
    State("severity-filter", "value"),
    prevent_initial_call=True
)
def handle_chat(send_clicks, n_submit, user_input, conversation_history, 
                years, types, sectors, companies, severities):
    if not user_input or user_input.strip() == "":
        return dash.no_update, dash.no_update, dash.no_update
    
    # Filter data based on current filters
    df = companies_df.copy()
    if years:
        df = df[df["Year"].isin(years)]
    if types:
        df = df[df["Type"].isin(types)]
    if sectors:
        df = df[df["Sector"].isin(sectors)]
    if companies:
        df = df[df["Company"].isin(companies)]
    if severities:
        df = df[df["Severity"].isin(severities)]
    
    if df.empty:
        error_msg = html.Div([
            html.Div("⚠️ Nessun dato disponibile con i filtri correnti. Modifica i filtri per continuare.",
                     style={
                         "backgroundColor": "#fff3cd",
                         "color": "#856404",
                         "padding": "12px 16px",
                         "borderRadius": "12px",
                         "marginBottom": "12px",
                         "border": "1px solid #ffeeba",
                         "maxWidth": "80%"
                     })
        ])
        return error_msg, conversation_history, ""
    
    # Initialize RAG system
    rag = BlindSpotRAG()
    
    # Get AI response
    try:
        ai_response = rag.chat(df, kpi_df, conversation_history, user_input)
        
        # Update conversation history
        new_history = conversation_history + [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": ai_response}
        ]
        
        # Build chat UI - Initial message
        chat_messages = [
            html.Div([
                html.Div("👋 Ciao! Sono Ada, l'assistente AI del progetto Blind Spot.", 
                         className="assistant-message chat-message",
                         style={
                             "backgroundColor": "#ffffff",
                             "padding": "12px 16px",
                             "borderRadius": "12px",
                             "marginBottom": "12px",
                             "maxWidth": "80%",
                             "border": "1px solid #e5e7eb",
                             "boxShadow": "0 2px 4px rgba(0,0,0,0.05)"
                         }),
                html.Div("Posso aiutarti ad analizzare i dati sulla trasparenza di genere. Prova a chiedermi:", 
                         className="assistant-message chat-message",
                         style={
                             "backgroundColor": "#ffffff",
                             "padding": "12px 16px",
                             "borderRadius": "12px",
                             "marginBottom": "8px",
                             "maxWidth": "80%",
                             "border": "1px solid #e5e7eb",
                             "boxShadow": "0 2px 4px rgba(0,0,0,0.05)"
                         }),
                html.Ul([
                    html.Li("Qual è l'azienda più trasparente?"),
                    html.Li("Come si comporta il settore tecnologico?"),
                    html.Li("Ci sono stati miglioramenti nel tempo?"),
                    html.Li("Quali KPI mancano più spesso?"),
                ], style={"color": "#5b6475", "fontSize": "0.85rem", "marginLeft": "30px"})
            ])
        ]
        
        # Add conversation messages
        for i in range(0, len(new_history), 2):
            if i < len(new_history):
                # User message
                chat_messages.append(
                    html.Div(new_history[i]["content"],
                             className="user-message chat-message",
                             style={
                                 "backgroundColor": "#0f766e",
                                 "color": "white",
                                 "padding": "12px 16px",
                                 "borderRadius": "12px",
                                 "marginBottom": "12px",
                                 "marginLeft": "auto",
                                 "maxWidth": "80%",
                                 "textAlign": "right",
                                 "boxShadow": "0 2px 8px rgba(15, 118, 110, 0.2)"
                             })
                )
            
            if i + 1 < len(new_history):
                # Assistant message
                chat_messages.append(
                    html.Div(
                        dcc.Markdown(new_history[i + 1]["content"]),
                        className="assistant-message chat-message",
                        style={
                            "backgroundColor": "#ffffff",
                            "padding": "12px 16px",
                            "borderRadius": "12px",
                            "marginBottom": "12px",
                            "maxWidth": "80%",
                            "border": "1px solid #e5e7eb",
                            "boxShadow": "0 2px 4px rgba(0,0,0,0.05)"
                        }
                    )
                )
        
        return chat_messages, new_history, ""
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        error_msg = html.Div([

            html.Div(f"❌ Errore: {str(e)}",
                     style={
                         "backgroundColor": "#f8d7da",
                         "color": "#721c24",
                         "padding": "12px 16px",
                         "borderRadius": "12px",
                         "marginBottom": "12px",
                         "border": "1px solid #f5c6cb",
                         "maxWidth": "80%"
                     })
        ])
        return error_msg, conversation_history, ""

@app.callback(
    Output("chat-send-btn", "className"),
    Input("chat-send-btn", "n_clicks"),
    prevent_initial_call=True
)
def add_sending_animation(n_clicks):
    if n_clicks and n_clicks > 0:
        return "sending"
    return ""

# Chatbot UI
chatbot_container = html.Div([
    html.Div([
        html.H5("💬 AI Assistant", style={"fontWeight": "700", "color": "#0f766e", "marginBottom": "12px"}),
        html.P("Fai domande sui dati visualizzati. L'assistente risponderà in base ai filtri applicati.", 
               style={"fontSize": "0.9rem", "color": "#5b6475", "marginBottom": "20px"}),
    ]),
    
    # Chat messages container
    html.Div(id="chat-messages", style={
        "height": "500px",
        "overflowY": "auto",
        "backgroundColor": "#f8fafc",
        "borderRadius": "12px",
        "padding": "20px",
        "marginBottom": "16px",
        "border": "1px solid #e5e7eb"
    }, children=[
        html.Div([
            html.Div("👋 Ciao! Sono l'assistente AI del progetto Blind Spot.", 
                     className="assistant-message chat-message",
                     style={
                         "backgroundColor": "#ffffff",
                         "padding": "12px 16px",
                         "borderRadius": "12px",
                         "marginBottom": "12px",
                         "maxWidth": "80%",
                         "border": "1px solid #e5e7eb",
                         "boxShadow": "0 2px 4px rgba(0,0,0,0.05)"
                     }),
            html.Div("Posso aiutarti ad analizzare i dati sulla trasparenza di genere. Prova a chiedermi:", 
                     className="assistant-message chat-message",
                     style={
                         "backgroundColor": "#ffffff",
                         "padding": "12px 16px",
                         "borderRadius": "12px",
                         "marginBottom": "8px",
                         "maxWidth": "80%",
                         "border": "1px solid #e5e7eb",
                         "boxShadow": "0 2px 4px rgba(0,0,0,0.05)"
                     }),
            html.Ul([
                html.Li("Qual è l'azienda più trasparente?"),
                html.Li("Come si comporta il settore tecnologico?"),
                html.Li("Ci sono stati miglioramenti nel tempo?"),
                html.Li("Quali KPI mancano più spesso?"),
            ], style={"color": "#5b6475", "fontSize": "0.85rem", "marginLeft": "30px"})
        ])
    ]),
    
    # Input area
    dbc.Row([
        dbc.Col([
            dcc.Input(
                id="chat-input",
                type="text",
                placeholder="Scrivi la tua domanda...",
                style={
                    "width": "100%",
                    "padding": "12px 16px",
                    "borderRadius": "10px",
                    "border": "1px solid #e5e7eb",
                    "fontSize": "0.95rem"
                },
                n_submit=0
            )
        ], width=10),
        dbc.Col([
            dbc.Button(
                "Invia",
                id="chat-send-btn",
                color="primary",
                className="w-100",
                style={"padding": "12px"}
            )
        ], width=2)
    ]),
    
    # Hidden store for conversation history
    dcc.Store(id="conversation-store", data=[]),
    
    # Loading indicator
    dbc.Spinner(
        html.Div(id="chat-loading", style={"display": "none"}),
        color="success",
        type="grow",
        size="sm"
    )
], style={"padding": "20px"})


# ---------------------
# Server entrypoint
# ---------------------
if __name__ == "__main__":
    print("The Blind Spot dashboard is running at http://127.0.0.1:8050")
    app.run(debug=True, port=8050)
