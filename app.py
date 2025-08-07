import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import datetime

# Set page config
st.set_page_config(
    page_title="Sample Dashboard with PDF Export",
    page_icon="📊",
    layout="wide"
)

class DashboardPDF(FPDF):
    """Custom PDF class for dashboard export"""
    
    def __init__(self):
        super().__init__('P', 'in', (8.5, 11))  # Portrait, inches, Letter size
        self.set_margins(0.5, 0.5, 0.5)  # 0.5 inch margins
        self.set_auto_page_break(auto=True, margin=0.5)
    
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 0.3, 'Dashboard Report', 0, 1, 'C')
        self.ln(0.1)
    
    def footer(self):
        self.set_y(-0.5)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 0.2, f'Page {self.page_no()} - Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')

def create_sample_data():
    """Generate sample data for the dashboard"""
    np.random.seed(42)
    
    # Sales data
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    sales_data = pd.DataFrame({
        'Date': dates,
        'Revenue': np.random.normal(5000, 1000, 30).round(2),
        'Orders': np.random.poisson(50, 30),
        'Customers': np.random.poisson(35, 30)
    })
    
    # Product performance data
    products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    product_data = pd.DataFrame({
        'Product': products,
        'Sales': np.random.uniform(10000, 50000, 5).round(2),
        'Units Sold': np.random.randint(100, 1000, 5),
        'Rating': np.random.uniform(3.5, 5.0, 5).round(1)
    })
    
    return sales_data, product_data

def create_charts(sales_data, product_data):
    """Create matplotlib charts for PDF export"""
    charts = {}
    
    # Sales trend chart
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    ax1.plot(sales_data['Date'], sales_data['Revenue'], marker='o', linewidth=2, markersize=4)
    ax1.set_title('Daily Revenue Trend', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Revenue ($)')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    
    # Save to bytes
    buffer1 = io.BytesIO()
    plt.savefig(buffer1, format='png', dpi=150, bbox_inches='tight')
    buffer1.seek(0)
    charts['revenue_trend'] = buffer1
    plt.close()
    
    # Product sales bar chart
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    bars = ax2.bar(product_data['Product'], product_data['Sales'], color='skyblue', edgecolor='navy', alpha=0.7)
    ax2.set_title('Product Sales Comparison', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Product')
    ax2.set_ylabel('Sales ($)')
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:,.0f}', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Save to bytes
    buffer2 = io.BytesIO()
    plt.savefig(buffer2, format='png', dpi=150, bbox_inches='tight')
    buffer2.seek(0)
    charts['product_sales'] = buffer2
    plt.close()
    
    return charts

def generate_dashboard_pdf(sales_data, product_data, user_notes, charts):
    """Generate PDF report of the dashboard"""
    pdf = DashboardPDF()
    pdf.add_page()
    
    # Title and date
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 0.4, 'Business Dashboard Report', 0, 1, 'C')
    pdf.ln(0.2)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 0.2, f"Report generated on: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 0, 1, 'C')
    pdf.ln(0.3)
    
    # Executive Summary
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 0.3, 'Executive Summary', 0, 1)
    pdf.ln(0.1)
    
    pdf.set_font('Arial', '', 12)
    summary_text = f"""
This dashboard report provides insights into business performance for the period {sales_data['Date'].min().strftime('%B %d')} to {sales_data['Date'].max().strftime('%B %d, %Y')}.

Key Metrics:
{chr(149)} Total Revenue: ${sales_data['Revenue'].sum():,.2f}
{chr(149)} Average Daily Revenue: ${sales_data['Revenue'].mean():,.2f}
{chr(149)} Total Orders: {sales_data['Orders'].sum():,}
{chr(149)} Total Customers Served: {sales_data['Customers'].sum():,}
{chr(149)} Top Performing Product: {product_data.loc[product_data['Sales'].idxmax(), 'Product']}
"""
    
    pdf.multi_cell(0, 0.2, summary_text.strip())
    pdf.ln(0.2)
    
    # Revenue Trend Chart
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 0.3, 'Revenue Trend Analysis', 0, 1)
    pdf.ln(0.1)
    
    # Save chart as temporary file
    with open('temp_revenue_chart.png', 'wb') as f:
        f.write(charts['revenue_trend'].getvalue())
    
    # Add chart to PDF
    chart_width = 6.5
    chart_height = 3.7
    x_pos = (8.5 - chart_width) / 2
    
    pdf.image('temp_revenue_chart.png', x=x_pos, y=pdf.get_y(), w=chart_width, h=chart_height)
    pdf.ln(chart_height + 0.3)
    
    # Product Performance Table
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 0.3, 'Product Performance', 0, 1)
    pdf.ln(0.1)

    # Table headers
    pdf.set_font('Arial', 'B', 11)
    col_widths = [1.8, 1.5, 1.5, 1.2]
    headers = ['Product', 'Sales ($)', 'Units Sold', 'Rating']
    
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 0.25, header, 1, 0, 'C')
    pdf.ln()
    
    # Table data
    pdf.set_font('Arial', '', 10)
    for _, row in product_data.iterrows():
        product_name = clean_text_for_pdf(str(row['Product']))
        pdf.cell(col_widths[0], 0.25, product_name, 1, 0, 'L')
        pdf.cell(col_widths[1], 0.25, f"${row['Sales']:,.0f}", 1, 0, 'R')
        pdf.cell(col_widths[2], 0.25, f"{row['Units Sold']:,}", 1, 0, 'C')
        pdf.cell(col_widths[3], 0.25, f"{row['Rating']}", 1, 0, 'C')
        pdf.ln()
    
    pdf.ln(0.3)
    
    # Product Sales Chart
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 0.3, 'Product Sales Comparison', 0, 1)
    pdf.ln(0.1)
    
    # Save chart as temporary file
    with open('temp_product_chart.png', 'wb') as f:
        f.write(charts['product_sales'].getvalue())
    
    pdf.image('temp_product_chart.png', x=x_pos, y=pdf.get_y(), w=chart_width, h=chart_height)
    pdf.ln(chart_height + 0.3)
    
    # User Notes
    if user_notes and user_notes.strip():
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 0.3, 'Additional Notes', 0, 1)
        pdf.ln(0.1)
        
        pdf.set_font('Arial', '', 12)
        cleaned_notes = clean_text_for_pdf(user_notes.strip())
        pdf.multi_cell(0, 0.2, cleaned_notes)
    
    # Cleanup temporary files
    import os
    for temp_file in ['temp_revenue_chart.png', 'temp_product_chart.png']:
        try:
            os.remove(temp_file)
        except:
            pass
    
    return pdf

def clean_text_for_pdf(text):
    """Clean text to ensure it's compatible with Latin-1 encoding"""
    if not text:
        return text
    
    # Replace common Unicode characters with Latin-1 compatible ones
    replacements = {
        '\u2022': chr(149),  # bullet point
        '\u2013': '-',       # en dash
        '\u2014': '--',      # em dash
        '\u2018': "'",       # left single quote
        '\u2019': "'",       # right single quote
        '\u201C': '"',       # left double quote
        '\u201D': '"',       # right double quote
        '\u2026': '...',     # ellipsis
    }
    
    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)
    
    # Remove any remaining non-Latin-1 characters
    try:
        text.encode('latin-1')
        return text
    except UnicodeEncodeError:
        # If there are still encoding issues, replace problematic characters
        return text.encode('latin-1', errors='replace').decode('latin-1')

def get_pdf_bytes(pdf):
    """Convert PDF to bytes for download"""
    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, str):
        return pdf_output.encode('latin-1')
    elif isinstance(pdf_output, bytearray):
        return bytes(pdf_output)
    else:
        return pdf_output

def main():
    # Page title
    st.title("📊 Business Dashboard")
    st.markdown("**Interactive dashboard with PDF export capability**")
    st.markdown("---")
    
    # Generate sample data
    sales_data, product_data = create_sample_data()
    
    # Sidebar controls
    st.sidebar.header("📋 Dashboard Controls")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select date range:",
        value=(sales_data['Date'].min(), sales_data['Date'].max()),
        min_value=sales_data['Date'].min(),
        max_value=sales_data['Date'].max()
    )
    
    # Filter data based on date range
    if len(date_range) == 2:
        mask = (sales_data['Date'] >= pd.Timestamp(date_range[0])) & (sales_data['Date'] <= pd.Timestamp(date_range[1]))
        filtered_sales = sales_data[mask]
    else:
        filtered_sales = sales_data
    
    # Product filter
    selected_products = st.sidebar.multiselect(
        "Select products to display:",
        options=product_data['Product'].tolist(),
        default=product_data['Product'].tolist()
    )
    
    filtered_products = product_data[product_data['Product'].isin(selected_products)]
    
    # Main dashboard layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Revenue Trend")
        st.line_chart(filtered_sales.set_index('Date')['Revenue'])
        
        st.subheader("📊 Product Sales")
        st.bar_chart(filtered_products.set_index('Product')['Sales'])
    
    with col2:
        st.subheader("📋 Key Metrics")
        
        # Metrics cards
        total_revenue = filtered_sales['Revenue'].sum()
        avg_revenue = filtered_sales['Revenue'].mean()
        total_orders = filtered_sales['Orders'].sum()
        
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
        st.metric("Avg Daily Revenue", f"${avg_revenue:,.2f}")
        st.metric("Total Orders", f"{total_orders:,}")
        
        if not filtered_products.empty:
            top_product = filtered_products.loc[filtered_products['Sales'].idxmax(), 'Product']
            st.metric("Top Product", top_product)
    
    # Data tables
    st.subheader("📋 Detailed Data")
    
    tab1, tab2 = st.tabs(["Sales Data", "Product Performance"])
    
    with tab1:
        st.dataframe(filtered_sales, use_container_width=True)
    
    with tab2:
        st.dataframe(filtered_products, use_container_width=True)
    
    # User notes section
    st.subheader("📝 Additional Notes")
    user_notes = st.text_area(
        "Add your observations, insights, or comments here:",
        placeholder="Enter any additional notes, observations, or insights you'd like to include in the PDF report...",
        height=120
    )
    
    # PDF Export section
    st.markdown("---")
    st.subheader("📄 Export Dashboard")
    
    # Initialize session state
    if 'pdf_data' not in st.session_state:
        st.session_state.pdf_data = None
        st.session_state.pdf_filename = None
    
    # Generate PDF button
    if st.button("🚀 Generate PDF Report", type="primary", use_container_width=True):
        with st.spinner("Generating PDF report..."):
            try:
                # Create charts for PDF
                charts = create_charts(filtered_sales, filtered_products)
                
                # Generate PDF
                pdf = generate_dashboard_pdf(filtered_sales, filtered_products, user_notes, charts)
                
                # Convert to bytes
                pdf_bytes = get_pdf_bytes(pdf)
                
                # Create filename
                filename = f"Dashboard_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                # Store in session state
                st.session_state.pdf_data = pdf_bytes
                st.session_state.pdf_filename = filename
                
                st.success("✅ PDF report generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating PDF: {str(e)}")
    
    # Download button
    if st.session_state.pdf_data is not None:
        st.download_button(
            label="📄 Download PDF Report",
            data=st.session_state.pdf_data,
            file_name=st.session_state.pdf_filename,
            mime="application/pdf",
            type="secondary",
            use_container_width=True
        )
        
        # PDF info
        st.info(f"""
        **📋 PDF Report Information:**
        - **Filename:** {st.session_state.pdf_filename}
        - **Format:** 8.5 x 11 inches (Letter size)
        - **Content:** Charts, tables, metrics, and notes
        - **Ready for printing!**
        """)
    
    # Instructions
    with st.expander("ℹ️ How to use this dashboard"):
        st.markdown("""
        ### Dashboard Features:
        1. **Interactive Filters**: Use the sidebar to filter data by date range and products
        2. **Real-time Charts**: Charts update automatically based on your selections  
        3. **Data Tables**: View detailed data in the tabs below
        4. **Custom Notes**: Add your insights in the text area
        5. **PDF Export**: Generate a professional PDF report with all content
        
        ### PDF Export Process:
        1. Configure your filters and add notes
        2. Click "Generate PDF Report" 
        3. Click "Download PDF Report" when ready
        4. Open and print your professional report!
        
        The PDF includes all charts, tables, metrics, and your notes formatted for 8.5x11 inch paper.
        """)

if __name__ == "__main__":
    main() 
