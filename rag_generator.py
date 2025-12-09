import os
import re
import pandas as pd
from datetime import datetime
from typing import Dict, List
import openai
from dotenv import load_dotenv
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class BlindSpotRAG:
    """
    RAG system for generating narrative reports based on filtered dashboard data.
    Uses retrieval-augmented generation with OpenAI to create context-aware narratives.
    """
    
    def __init__(self):
        self.severity_descriptions = {
            "Trasparente": {
                "level": "Minimal omissions",
                "interpretation": "The company demonstrates excellent transparency with minimal gaps.",
                "recommendation": "Continue current practices and share best practices with peers."
            },
            "Bassa": {
                "level": "Low omission level",
                "interpretation": "The company shows good transparency with few gaps.",
                "recommendation": "Address the remaining gaps through targeted improvements."
            },
            "Moderata": {
                "level": "Moderate omissions",
                "interpretation": "The company has several important KPIs missing.",
                "recommendation": "Implement a structured plan to address missing KPIs."
            },
            "Grave": {
                "level": "Severe omissions",
                "interpretation": "The company has significant gaps including essential KPIs.",
                "recommendation": "Urgent action needed to improve transparency."
            },
            "Critica": {
                "level": "Critical omissions",
                "interpretation": "Fundamental KPIs are missing from reporting.",
                "recommendation": "Comprehensive overhaul of reporting framework essential."
            },
            "Estrema": {
                "level": "Extreme omissions",
                "interpretation": "The company omits almost all critical areas.",
                "recommendation": "Immediate intervention required."
            }
        }
    
    def _build_context(self, df: pd.DataFrame, kpi_df: pd.DataFrame = None) -> str:
        """Build context from filtered data for RAG retrieval."""
        context_parts = []
        
        # Calculate unique companies vs total entries
        unique_companies = df['Company'].nunique() if 'Company' in df.columns else len(df)
        total_entries = len(df)
        
        # Filter out entries with OSS = 0 (no DNF available)
        df_with_data = df[df['Total_OSS_Score'] > 0] if 'Total_OSS_Score' in df.columns else df
        entries_no_data = total_entries - len(df_with_data)
        
        context_parts.append("=== DATASET SUMMARY ===")
        context_parts.append(f"Unique companies: {unique_companies}")
        context_parts.append(f"Total company-year entries analyzed: {total_entries}")
        if entries_no_data > 0:
            context_parts.append(f"⚠️ Entries with no DNF available (OSS=0): {entries_no_data}")
            context_parts.append(f"Entries with DNF data: {len(df_with_data)}")
        
        # Add year distribution if available
        if "Year" in df.columns and df["Year"].nunique() > 0:
            year_counts = df["Year"].value_counts().sort_index()
            context_parts.append(f"Years covered: {', '.join(map(str, sorted(df['Year'].unique())))}")
            for year, count in year_counts.items():
                context_parts.append(f"  - Year {year}: {count} entries")
        
        # Use df_with_data for statistics
        if len(df_with_data) > 0:
            context_parts.append(f"\nAverage OSS Score (excluding N/A): {df_with_data['Total_OSS_Score'].mean():.2f}")
            context_parts.append(f"Median OSS Score (excluding N/A): {df_with_data['Total_OSS_Score'].median():.2f}")
            context_parts.append(f"Min OSS Score: {df_with_data['Total_OSS_Score'].min():.2f}")
            context_parts.append(f"Max OSS Score: {df_with_data['Total_OSS_Score'].max():.2f}")
        
        context_parts.append("\n=== SEVERITY DISTRIBUTION ===")
        severity_counts = df["Severity"].value_counts()
        for severity, count in severity_counts.items():
            pct = (count / len(df) * 100)
            if severity == "N/A":
                context_parts.append(f"{severity} (No DNF available): {count} entries ({pct:.1f}%)")
            else:
                context_parts.append(f"{severity}: {count} entries ({pct:.1f}%)")
        
        if "Sector" in df.columns and df["Sector"].nunique() > 0:
            context_parts.append("\n=== SECTOR DISTRIBUTION ===")
            sector_stats = df_with_data.groupby("Sector")["Total_OSS_Score"].agg(['count', 'mean', 'min', 'max']) if len(df_with_data) > 0 else pd.DataFrame()
            for sector, row in sector_stats.iterrows():
                context_parts.append(f"{sector}: {int(row['count'])} entries, avg OSS: {row['mean']:.2f}")
        
        if "Type" in df.columns and df["Type"].nunique() > 0:
            context_parts.append("\n=== COMPANY TYPE DISTRIBUTION ===")
            type_stats = df_with_data.groupby("Type")["Total_OSS_Score"].agg(['count', 'mean']) if len(df_with_data) > 0 else pd.DataFrame()
            for comp_type, row in type_stats.iterrows():
                context_parts.append(f"{comp_type}: {int(row['count'])} entries, avg OSS: {row['mean']:.2f}")
        
        if len(df_with_data) > 0:
            context_parts.append("\n=== TOP AND BOTTOM PERFORMERS ===")
            context_parts.append("Most Transparent (Lowest OSS - excluding companies with no DNF):")
            for idx, row in df_with_data.nsmallest(3, 'Total_OSS_Score')[['Company', 'Total_OSS_Score', 'Severity', 'Year']].iterrows():
                year_info = f" ({int(row['Year'])})" if 'Year' in row and pd.notna(row['Year']) else ""
                context_parts.append(f"  - {row['Company']}{year_info}: {row['Total_OSS_Score']:.2f} ({row['Severity']})")
            
            context_parts.append("\nLeast Transparent (Highest OSS):")
            for idx, row in df_with_data.nlargest(3, 'Total_OSS_Score')[['Company', 'Total_OSS_Score', 'Severity', 'Year']].iterrows():
                year_info = f" ({int(row['Year'])})" if 'Year' in row and pd.notna(row['Year']) else ""
                context_parts.append(f"  - {row['Company']}{year_info}: {row['Total_OSS_Score']:.2f} ({row['Severity']})")
        
        return "\n".join(context_parts)
    
    def generate_report(self, df: pd.DataFrame, kpi_df: pd.DataFrame = None, 
                       filters: Dict = None) -> str:
        """Generate a narrative report using RAG approach."""
        if df.empty:
            return "No data available for report generation."
        
        context = self._build_context(df, kpi_df)
        
        filter_summary = "All Data"
        if filters:
            filter_parts = []
            if filters.get('years'):
                filter_parts.append(f"Years: {', '.join(map(str, filters['years']))}")
            if filters.get('types'):
                filter_parts.append(f"Types: {', '.join(filters['types'])}")
            if filters.get('sectors'):
                filter_parts.append(f"Sectors: {', '.join(filters['sectors'])}")
            if filters.get('severities'):
                filter_parts.append(f"Severity Levels: {', '.join(filters['severities'])}")
            if filter_parts:
                filter_summary = " | ".join(filter_parts)
        
        prompt = self._create_prompt(context, filter_summary, len(df))
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert analyst specializing in gender equality and corporate transparency. 
Write professional, data-driven narrative reports about gender equality transparency based on provided data.
Be specific with numbers and percentages. Structure responses with clear sections."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def _create_prompt(self, context: str, filter_summary: str, num_companies: int) -> str:
        """Create the prompt for the RAG system."""
        prompt = f"""Based on the following data about gender equality transparency in corporate reporting, 
write a comprehensive narrative report.

IMPORTANT: The dataset tracks companies across multiple years. When you see "Unique companies: X" and "Total company-year entries: Y", 
this means X distinct companies are analyzed across multiple years, resulting in Y total data points. 
Always clarify this distinction in your report to avoid confusion.

FILTERS APPLIED: {filter_summary}

DATA CONTEXT:
{context}

REPORT STRUCTURE - Please include these sections:

1. EXECUTIVE SUMMARY
   - Clearly state the number of unique companies and the time period covered
   - Overview of transparency levels
   - Key findings

2. KEY FINDINGS
   - Analysis of severity distribution across company-years
   - Sector-specific insights
   - Notable trends over time

3. PERFORMANCE METRICS
   - Average transparency scores
   - Distribution analysis
   - Top and bottom performers (note the year for each)

4. SECTORAL ANALYSIS
   - How different sectors compare
   - Sector-specific challenges

5. RECOMMENDATIONS
   - Targeted improvements
   - Priority areas
   - Best practices

6. CONCLUSION
   - Summary of transparency status
   - Call to action

Write in professional language suitable for corporate stakeholders and regulators.
Use specific numbers and percentages from the data. When mentioning specific companies,
include the year of the data point for clarity."""
        
        return prompt
    
    def export_report_to_pdf(self, report_content: str, filename: str = None) -> bytes:
        """
        Export the generated report to PDF format.
        
        Args:
            report_content: The generated report content
            filename: Optional custom filename (for reference, returns bytes)
        
        Returns:
            PDF file as bytes
        """
        # Create PDF in memory
        pdf_buffer = BytesIO()
        
        # Define page size and margins
        pagesize = A4
        margin = 0.75 * inch
        width = pagesize[0] - 2 * margin
        height = pagesize[1] - 2 * margin
        
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=pagesize,
            rightMargin=margin,
            leftMargin=margin,
            topMargin=margin,
            bottomMargin=margin,
            title="The Blind Spot - Gender Equality Report"
        )
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#0f766e'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#5b6475'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0f766e'),
            spaceAfter=10,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderPadding=5,
            borderColor=colors.HexColor('#0f766e'),
            borderWidth=0,
            borderRadius=0
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#3a3f4b'),
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            leading=13
        )
        
        meta_style = ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#5b6475'),
            alignment=TA_LEFT,
            spaceAfter=6
        )
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER
        )
        
        # Build PDF content
        story = []
        
        # Title section
        story.append(Paragraph("The Blind Spot", title_style))
        story.append(Paragraph("Gender Equality Transparency Analysis", subtitle_style))
        
        # Metadata
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style))
        story.append(Paragraph(f"<b>Framework:</b> Omission Severity Score (OSS) Analysis", meta_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # Parse report content and add to PDF
        lines = report_content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if not line:
                story.append(Spacer(1, 0.1 * inch))
                continue
            
            # Detect section headers (lines ending with :)
            if line.endswith(':') and len(line) > 2:
                story.append(Paragraph(line, heading_style))
                story.append(Spacer(1, 0.08 * inch))
            # Detect list items
            elif line.startswith('- '):
                bullet_text = line[2:]
                story.append(Paragraph(f"• {bullet_text}", body_style))
            elif line.startswith('* '):
                bullet_text = line[2:]
                story.append(Paragraph(f"• {bullet_text}", body_style))
            # Regular paragraphs
            else:
                story.append(Paragraph(line, body_style))
        
        # Add footer with logo
        story.append(Spacer(1, 0.3 * inch))
        
        # Horizontal line
        story.append(Paragraph(
            "<hr width='100%' color='#e5e7eb'/>",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.15 * inch))
        
        # Try to add logo if available
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "team=logo.png")
        if os.path.exists(logo_path):
            try:
                # Create image object with appropriate size
                logo = Image(logo_path, width=2*inch, height=0.6*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 0.1 * inch))
            except Exception as e:
                print(f"Could not load logo: {e}")
        
        # Footer text
        story.append(Paragraph(
            "&copy; 2025 The Blind Spot Project. Making the invisible visible.",
            footer_style
        ))
        story.append(Paragraph(
            "Analyzing gender equality reporting transparency.",
            footer_style
        ))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    def export_report_to_file(self, report_content: str, filename: str = None) -> str:
        """Export the generated report to a text file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"blind_spot_report_{timestamp}.txt"
        
        filepath = os.path.join(os.getcwd(), filename)
        
        header = f"""
{'='*80}
THE BLIND SPOT - GENDER EQUALITY TRANSPARENCY REPORT
{'='*80}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{'='*80}

"""
        footer = f"""

{'='*80}
End of Report
{'='*80}
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write(report_content)
            f.write(footer)
        
        return filepath
    
    def export_report_to_html(self, report_content: str, filename: str = None) -> str:
        """
        Export the generated report as HTML for better formatting.
        
        Args:
            report_content: The generated report content
            filename: Optional custom filename
        
        Returns:
            Path to the saved HTML file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"blind_spot_report_{timestamp}.html"
        
        filepath = os.path.join(os.getcwd(), filename)
        
        # Convert simple markdown to HTML
        html_content = self._markdown_to_html(report_content)
        
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Blind Spot - Gender Equality Transparency Report</title>
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #0b1220;
            background: #f4f6f9;
            padding: 40px;
            max-width: 900px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #0f766e 0%, #1a9a8f 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 40px;
            box-shadow: 0 12px 36px rgba(15,23,42,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5rem;
            font-weight: 800;
        }}
        .header p {{
            margin: 0;
            font-size: 1.1rem;
            opacity: 0.95;
        }}
        .metadata {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 4px solid #0f766e;
            font-size: 0.9rem;
            color: #5b6475;
        }}
        .content {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(15,23,42,0.05);
        }}
        h2 {{
            color: #0f766e;
            border-bottom: 2px solid #0f766e;
            padding-bottom: 12px;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.8rem;
        }}
        h2:first-child {{
            margin-top: 0;
        }}
        h3 {{
            color: #2c4a5a;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.2rem;
        }}
        p {{
            margin-bottom: 15px;
            color: #3a3f4b;
        }}
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        li {{
            margin-bottom: 10px;
            color: #3a3f4b;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            color: #5b6475;
            font-size: 0.9rem;
        }}
        .highlight {{
            background-color: rgba(15,118,110,0.1);
            padding: 20px;
            border-left: 4px solid #0f766e;
            margin: 20px 0;
            border-radius: 4px;
        }}
        strong {{
            color: #0f766e;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>The Blind Spot</h1>
        <p>Gender Equality Transparency Analysis Report</p>
    </div>
    
    <div class="metadata">
        <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
        <strong>Framework:</strong> Omission Severity Score (OSS) Analysis
    </div>
    
    <div class="content">
        {html_content}
    </div>
    
    <div class="footer">
        <p>&copy; 2025 The Blind Spot Project. All rights reserved.</p>
        <p>Making the invisible visible: Analyzing gender equality reporting transparency.</p>
    </div>
</body>
</html>"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        return filepath
    
    def _markdown_to_html(self, text: str) -> str:
        """
        Convert simple markdown formatting to HTML.
        
        Args:
            text: Markdown text
        
        Returns:
            HTML formatted text
        """
        # Convert headers
        text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        
        # Convert bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        
        # Convert italic
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
        
        # Convert paragraphs
        paragraphs = text.split('\n\n')
        html_paragraphs = []
        
        for para in paragraphs:
            if para.strip().startswith('<'):
                html_paragraphs.append(para)
            elif para.strip():
                html_paragraphs.append(f'<p>{para.strip()}</p>')
        
        return '\n'.join(html_paragraphs)

    def chat(self, df: pd.DataFrame, kpi_df: pd.DataFrame, conversation_history: List[Dict], 
             user_message: str) -> str:
        """
        Chat with the AI assistant about the data.
        
        Args:
            df: Filtered companies dataframe
            kpi_df: KPI definitions dataframe
            conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
            user_message: The user's new message
            
        Returns:
            Assistant's response
        """
        # Build context from current data
        context = self._build_context(df, kpi_df)
        
        # Build system message with context
        system_message = f"""You are an AI assistant specialized in gender equality transparency analysis. 
You help users understand data from "The Blind Spot" project, which tracks gender equality KPI disclosure in corporate reports.

CURRENT DATA CONTEXT:
{context}

KEY CONCEPTS:
- OSS (Omission Severity Score): Higher = less transparent (range 0-185)
- **IMPORTANT**: OSS = 0 or Severity = "N/A" means the company's DNF (Non-Financial Declaration) is NOT AVAILABLE, not that they are transparent
- Only companies with OSS > 0 have available DNF data and can be analyzed for transparency
- Severity Levels (for companies WITH DNF):
  * Trasparente (1-31): Minimal omissions, excellent transparency
  * Bassa (32-62): Low omission level, good transparency
  * Moderata (63-93): Moderate omissions
  * Grave (94-124): Severe omissions
  * Critica (125-155): Critical omissions
  * Estrema (156-185): Extreme omissions
- KPI Categories: Board & Governance, Management, Pay Equity, STEM & Strategy, Work-Life Balance, Inclusion Culture

GUIDELINES:
- NEVER describe companies with OSS=0 or Severity="N/A" as "transparent" - they have no data available
- When ranking companies, exclude those with OSS=0 (no DNF available)
- Answer questions based on the current filtered data shown above
- Be specific with numbers, percentages, and company names
- If data is insufficient, clearly state limitations
- Suggest relevant visualizations when appropriate
- Keep responses concise but informative (max 200 words)
- Respond in the same language as the user (Italian or English)
- Use markdown formatting for better readability"""

        # Build messages for API
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history (limit to last 10 messages to avoid token limits)
        if conversation_history:
            messages.extend(conversation_history[-10:])
        
        # Add new user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=800,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Mi dispiace, si è verificato un errore: {str(e)}"


if __name__ == "__main__":
    rag = BlindSpotRAG()
    
    # Create sample data
    sample_df = pd.DataFrame({
        'Company': ['Company A', 'Company B', 'Company C'],
        'Sector': ['Technology', 'Finance', 'Energy'],
        'Type': ['Quotate', 'Non-Quotate', 'Quotate'],
        'Total_OSS_Score': [25.5, 68.3, 42.1],
        'Severity': ['Trasparente', 'Moderata', 'Bassa'],
        'Total_Missing_KPIs': [5, 12, 8]
    })
    
    # Generate report
    report = rag.generate_report(sample_df, filters={
        'types': ['Quotate'],
        'sectors': ['Technology']
    })
    
    print(report)