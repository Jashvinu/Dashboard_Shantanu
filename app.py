import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

try:
    import pandasai as pai
    
    # Set your PandaBI API key - get from https://app.pandabi.ai
    # First try to get from secrets, then environment, then allow manual entry
    PANDABI_API_KEY = st.secrets.get("PANDABI_API_KEY", os.environ.get("PANDABI_API_KEY", None))
    
    if PANDABI_API_KEY:
        pai.api_key.set(PANDABI_API_KEY)
        PANDAS_AI_AVAILABLE = True
    else:
        PANDAS_AI_AVAILABLE = False
        
except ImportError:
    PANDAS_AI_AVAILABLE = False

# Function to load data - keeping your existing function
@st.cache_data
def load_data():
    try:
        # Read the CSV file directly - assume it exists
        df = pd.read_csv("data.csv")

        # Clean up any currency symbols in numeric columns
        numeric_columns = ['Units Sold', 'Manufacturing Price', 'Sale Price',
                           'Gross Sales', 'Discounts', 'Sales', 'COGS', 'Profit',
                           'Month Number', 'Year']

        for col in numeric_columns:
            if col in df.columns:
                # Remove currency symbols and commas if present
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace(
                        r'[$,]', '', regex=True)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

        # Convert date column if it exists
        if 'Date' in df.columns:
            try:
                # Use explicit format to avoid warning
                df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
                df['Date'] = df['Date'].dt.date
            except:
                try:
                    # Try alternative format
                    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
                    df['Date'] = df['Date'].dt.date
                except:
                    pass

        return df
    except Exception as e:
        st.error(f"Error reading data.csv: {str(e)}")
        return pd.DataFrame()
# Page configuration

st.set_page_config(layout="wide")

# Import plotly.express to avoid using go directly

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #FAFAFA;
    }
    
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
    }
    
    .metric-container {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .project-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .status-badge {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
    }
    
    .on-track {
        background-color: #E5F7F0;
        color: #047857;
    }
    
    .delayed {
        background-color: #FEF3C7;
        color: #B45309;
    }
    
    .meeting-item {
        display: flex;
        align-items: center;
        padding: 10px 0;
    }
    
    .meeting-dot {
        width: 8px;
        height: 8px;
        background-color: #E5E7EB;
        border-radius: 50%;
        margin-right: 10px;
    }

    .document-item {
        display: flex;
        align-items: center;
        padding: 15px;
        background-color: white;
        border-radius: 8px;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .transaction-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #F3F4F6;
    }
    
    .positive-amount {
        color: #10B981;
    }
    
    .negative-amount {
        color: #EF4444;
    }

    .filter-container {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin: 10px 0;
    }

    .data-table-container {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Function to load data


@st.cache_data
def load_data():
    try:
        # Read the CSV file directly - assume it exists
        df = pd.read_csv("data.csv")

        # Clean up any currency symbols in numeric columns
        numeric_columns = ['Units Sold', 'Manufacturing Price', 'Sale Price',
                           'Gross Sales', 'Discounts', 'Sales', 'COGS', 'Profit',
                           'Month Number', 'Year']

        for col in numeric_columns:
            if col in df.columns:
                # Remove currency symbols and commas if present
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace(
                        r'[$,]', '', regex=True)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

        # Convert date column if it exists
        if 'Date' in df.columns:
            try:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df['Date'] = df['Date'].dt.date
            except:
                pass

        return df
    except Exception as e:
        st.error(f"Error reading data.csv: {str(e)}")
        return pd.DataFrame()
        # Create sample data based on provided example
        data = {
            'Segment': ['Government', 'Government', 'Midmarket'],
            'Country': ['Canada', 'Germany', 'France'],
            'Product': ['Carretera', 'Carretera', 'Carretera'],
            'Discount Band': ['None', 'None', 'None'],
            'Units Sold': [1618.5, 1321, 2178],
            'Manufacturing Price': [3.00, 3.00, 3.00],
            'Sale Price': [20.00, 20.00, 15.00],
            'Gross Sales': [32370.00, 26420.00, 32670.00],
            'Discounts': [0, 0, 0],
            'Sales': [32370.00, 26420.00, 32670.00],
            'COGS': [16185.00, 13210.00, 21780.00],
            'Profit': [16185.00, 13210.00, 10890.00],
            'Date': ['1/1/2014', '1/1/2014', '6/1/2014'],
            'Month Number': [1, 1, 6],
            'Month Name': ['January', 'January', 'June'],
            'Year': [2014, 2014, 2014]
        }
        df = pd.DataFrame(data)

        # Convert date strings to datetime objects
        try:
            df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y').dt.date
        except:
            try:
                df['Date'] = pd.to_datetime(
                    df['Date'], format='%d/%m/%Y').dt.date
            except:
                pass
        return df


# Header
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown("## Business Dashboard")
with col2:
    company = st.selectbox(
        "Select Company", ["Company 1", "Company 2", "Company 3"])

# Navigation tabs
tab1, tab2, tab3 = st.tabs(
    ["Project Management", "Finance & Reports", "Data Table"])

with tab1:
    # Metrics row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="metric-container">
                <p style="color: #6B7280; margin-bottom: 5px;">Total Projects</p>
                <h2 style="margin: 0;">24</h2>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="metric-container">
                <p style="color: #6B7280; margin-bottom: 5px;">Team Performance</p>
                <h2 style="margin: 0;">87%</h2>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="metric-container">
                <p style="color: #6B7280; margin-bottom: 5px;">Deadlines Met</p>
                <h2 style="margin: 0;">92%</h2>
            </div>
        """, unsafe_allow_html=True)

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Project Status")

        # Project 1
        st.markdown("""
            <div class="project-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0;">Website Redesign</h4>
                        <p style="color: #6B7280; margin: 5px 0;">Due: March 30, 2024</p>
                    </div>
                    <span class="status-badge on-track">On Track</span>
                </div>
                <div style="width: 100%; height: 8px; background-color: #F3F4F6; border-radius: 4px; margin-top: 10px;">
                    <div style="width: 75%; height: 100%; background-color: #10B981; border-radius: 4px;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Project 2
        st.markdown("""
            <div class="project-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0;">Mobile App Dev</h4>
                        <p style="color: #6B7280; margin: 5px 0;">Due: April 15, 2024</p>
                    </div>
                    <span class="status-badge delayed">Delayed</span>
                </div>
                <div style="width: 100%; height: 8px; background-color: #F3F4F6; border-radius: 4px; margin-top: 10px;">
                    <div style="width: 45%; height: 100%; background-color: #F59E0B; border-radius: 4px;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Project 3
        st.markdown("""
            <div class="project-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0;">CRM Integration</h4>
                        <p style="color: #6B7280; margin: 5px 0;">Due: March 25, 2024</p>
                    </div>
                    <span class="status-badge on-track">On Track</span>
                </div>
                <div style="width: 100%; height: 8px; background-color: #F3F4F6; border-radius: 4px; margin-top: 10px;">
                    <div style="width: 90%; height: 100%; background-color: #10B981; border-radius: 4px;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### Upcoming Schedule")

        st.markdown("""
            <div class="project-card">
                <div class="meeting-item">
                    <div class="meeting-dot"></div>
                    <div>
                        <h4 style="margin: 0;">Project Review</h4>
                        <p style="color: #6B7280; margin: 5px 0;">Today, 2:00 PM</p>
                    </div>
                </div>
                <div class="meeting-item">
                    <div class="meeting-dot"></div>
                    <div>
                        <h4 style="margin: 0;">Team Sync</h4>
                        <p style="color: #6B7280; margin: 5px 0;">Tomorrow, 11:00 AM</p>
                    </div>
                </div>
                <div class="meeting-item">
                    <div class="meeting-dot"></div>
                    <div>
                        <h4 style="margin: 0;">Client Meeting</h4>
                        <p style="color: #6B7280; margin: 5px 0;">Mar 25, 3:30 PM</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with tab2:
    # Metrics row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="metric-container">
                <p style="color: #6B7280; margin-bottom: 5px;">Total Revenue</p>
                <h2 style="margin: 0;">₹1,24,50,000</h2>
                <p style="color: #10B981; margin: 5px 0;">+8.5% vs last month</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="metric-container">
                <p style="color: #6B7280; margin-bottom: 5px;">Budget Utilized</p>
                <h2 style="margin: 0;">78%</h2>
                <p style="color: #6B7280; margin: 5px 0;">₹98,45,000 of ₹1,26,00,000</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="metric-container">
                <p style="color: #6B7280; margin-bottom: 5px;">Pending Approvals</p>
                <h2 style="margin: 0;">12</h2>
                <p style="color: #F59E0B; margin: 5px 0;">4 high priority</p>
            </div>
        """, unsafe_allow_html=True)

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Revenue vs Expenses")

        # Create sample data for the graph
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        revenue = [100, 120, 125, 130, 140, 160]
        expenses = [110, 105, 100, 95, 100, 105]

        # Create DataFrame for plotly express
        chart_data = pd.DataFrame({
            "Month": months,
            "Revenue": revenue,
            "Expenses": expenses
        })

        # Use plotly express instead of graph_objects
        fig = px.line(
            chart_data,
            x="Month",
            y=["Revenue", "Expenses"],
            color_discrete_map={"Revenue": "#10B981", "Expenses": "#F59E0B"}
        )

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#F3F4F6'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Recent Documents")

        st.markdown("""
            <div class="document-item">
                <div style="margin-right: 20px;">
                    <div style="width: 40px; height: 40px; background-color: #F3F4F6; border-radius: 4px;"></div>
                </div>
                <div style="flex-grow: 1;">
                    <h4 style="margin: 0;">Q1 Financial Report</h4>
                    <p style="color: #6B7280; margin: 5px 0;">Modified 2 days ago</p>
                </div>
                <div style="color: #6B7280;">PDF</div>
            </div>
            
            <div class="document-item">
                <div style="margin-right: 20px;">
                    <div style="width: 40px; height: 40px; background-color: #F3F4F6; border-radius: 4px;"></div>
                </div>
                <div style="flex-grow: 1;">
                    <h4 style="margin: 0;">Budget Analysis 2024</h4>
                    <p style="color: #6B7280; margin: 5px 0;">Modified 1 week ago</p>
                </div>
                <div style="color: #6B7280;">XLSX</div>
            </div>
            
            <div class="document-item">
                <div style="margin-right: 20px;">
                    <div style="width: 40px; height: 40px; background-color: #F3F4F6; border-radius: 4px;"></div>
                </div>
                <div style="flex-grow: 1;">
                    <h4 style="margin: 0;">Tax Documentation</h4>
                    <p style="color: #6B7280; margin: 5px 0;">Modified 3 days ago</p>
                </div>
                <div style="color: #6B7280;">PDF</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### Quick Links")

        st.markdown("""
            <div style="background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <div style="padding: 10px 0;"><a href="#" style="color: #111827; text-decoration: none;">HR Portal</a></div>
                <div style="padding: 10px 0;"><a href="#" style="color: #111827; text-decoration: none;">Finance Dashboard</a></div>
                <div style="padding: 10px 0;"><a href="#" style="color: #111827; text-decoration: none;">CRM System</a></div>
                <div style="padding: 10px 0;"><a href="#" style="color: #111827; text-decoration: none;">Policy Documents</a></div>
            </div>
        """, unsafe_allow_html=True)

        # Instead of using HTML markup, let's use Streamlit's native components
        st.markdown("### Recent Transactions")

        with st.container():
            # Create a white background container
            with st.container():
                st.markdown("""
                    <div style="background-color: white; padding: 15px; border-radius: 8px;">
                """, unsafe_allow_html=True)

                # Transaction 1
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("**Office Supplies**")
                    st.markdown(
                        "<span style='color: #6B7280;'>Mar 21, 2024</span>", unsafe_allow_html=True)
                with col2:
                    st.markdown(
                        "<div style='color: #EF4444; text-align: right;'>-₹12,500</div>", unsafe_allow_html=True)

                st.markdown(
                    "<hr style='margin: 10px 0; border-color: #F3F4F6;'>", unsafe_allow_html=True)

                # Transaction 2
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("**Client Payment**")
                    st.markdown(
                        "<span style='color: #6B7280;'>Mar 20, 2024</span>", unsafe_allow_html=True)
                with col2:
                    st.markdown(
                        "<div style='color: #10B981; text-align: right;'>+₹1,45,000</div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("## Data Table")

    # Load data
    df = load_data()

    # Create filter section
    st.markdown("### Filters")

    with st.container():
        st.markdown("""
            <div class="filter-container">
        """, unsafe_allow_html=True)

        # Display all unique columns with a selectbox for each
        columns_to_filter = ["Segment", "Country",
                             "Product", "Discount Band", "Month Name", "Year"]

        # Create two rows of filters with 3 columns each
        col1, col2, col3 = st.columns(3)
        col_map = {0: col1, 1: col2, 2: col3}

        filter_selections = {}

        for i, column in enumerate(columns_to_filter):
            col_idx = i % 3
            with col_map[col_idx]:
                # Get unique values and add "All" option
                unique_values = ["All"]
                if column in df.columns:
                    unique_values += sorted([str(x)
                                            for x in df[column].dropna().unique().tolist()])

                # Create the selectbox
                filter_selections[column] = st.selectbox(
                    f"Filter by {column}",
                    unique_values
                )

        # Add numeric range sliders in two columns
        col1, col2 = st.columns(2)

        with col1:
            # Units sold range slider
            min_units = float(df["Units Sold"].min()
                              ) if "Units Sold" in df.columns else 0
            max_units = float(df["Units Sold"].max()
                              ) if "Units Sold" in df.columns else 1000
            units_range = st.slider(
                "Units Sold Range", min_units, max_units, (min_units, max_units))

        with col2:
            # Profit range slider
            min_profit = float(df["Profit"].min()
                               ) if "Profit" in df.columns else 0
            max_profit = float(df["Profit"].max()
                               ) if "Profit" in df.columns else 100000
            profit_range = st.slider(
                "Profit Range", min_profit, max_profit, (min_profit, max_profit))

        col1, col2 = st.columns(2)

        with col1:
            # Date range for filter
            min_date = df["Date"].min(
            ) if "Date" in df.columns else datetime.now().date()
            max_date = df["Date"].max(
            ) if "Date" in df.columns else datetime.now().date()
            start_date = st.date_input("Start Date", min_date)

        with col2:
            end_date = st.date_input("End Date", max_date)

        # Add search box
        search_term = st.text_input("Search in any column", "")

        st.markdown("</div>", unsafe_allow_html=True)

    # Apply filters
    filtered_df = df.copy()

    # Filter by date
    if "Date" in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df["Date"] >= start_date) & (
            filtered_df["Date"] <= end_date)]

    # Apply all column filters
    for column, selection in filter_selections.items():
        if selection != "All" and column in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[column].astype(
                str) == selection]

    # Filter by units sold range
    if "Units Sold" in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df["Units Sold"] >= units_range[0]) &
                                  (filtered_df["Units Sold"] <= units_range[1])]

    # Filter by profit range
    if "Profit" in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df["Profit"] >= profit_range[0]) &
                                  (filtered_df["Profit"] <= profit_range[1])]

    # Apply search if entered
    if search_term:
        search_mask = filtered_df.astype(str).apply(
            lambda x: x.str.contains(search_term, case=False)).any(axis=1)
        filtered_df = filtered_df[search_mask]

    # Format the DataFrame for display
    display_df = filtered_df.copy()

    # Format currency columns
    currency_columns = ['Manufacturing Price', 'Sale Price', 'Gross Sales',
                        'Discounts', 'Sales', 'COGS', 'Profit']

    for col in currency_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda x: f"${x:,.2f}" if pd.notnull(x) else "")

    # Display filtered data
    st.markdown("### Results")

    with st.container():
        st.markdown("""
            <div class="data-table-container">
        """, unsafe_allow_html=True)

        # Show number of results
        st.write(f"Showing {len(filtered_df)} of {len(df)} entries")

        # Add column selection for the table
        all_columns = filtered_df.columns.tolist()
        with st.expander("Select columns to display"):
            selected_columns = st.multiselect(
                "Choose columns",
                options=all_columns,
                default=all_columns
            )

        # Display the data table with only selected columns
        if selected_columns:
            st.dataframe(display_df[selected_columns],
                         use_container_width=True)
        else:
            st.dataframe(display_df, use_container_width=True)

        # Download button for filtered data
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Data",
            data=csv,
            file_name="filtered_data.csv",
            mime="text/csv",
        )

        st.markdown("</div>", unsafe_allow_html=True)


# Allow users to upload their own CSV file
def convert_to_pai_dataframe(pandas_df):
    # Method 1: Save to temporary CSV and reload with PandasAI
    temp_file = "temp_data_for_pai.csv"
    pandas_df.to_csv(temp_file, index=False)
    pai_df = pai.read_csv(temp_file)
    # Clean up temp file (optional)
    # import os
    # os.remove(temp_file)
    return pai_df

# Add this to the sidebar section of your dashboard
def fallback_analysis(df, query):
    """Provide basic analysis when PandasAI fails"""
    query = query.lower()
    
    if "total" in query and any(col in query for col in df.columns):
        # Try to identify which column to sum
        for col in df.columns:
            if col.lower() in query and pd.api.types.is_numeric_dtype(df[col]):
                return f"Total {col}: {df[col].sum()}"
    
    elif "average" in query or "mean" in query:
        for col in df.columns:
            if col.lower() in query and pd.api.types.is_numeric_dtype(df[col]):
                return f"Average {col}: {df[col].mean()}"
    
    elif "maximum" in query or "highest" in query:
        for col in df.columns:
            if col.lower() in query and pd.api.types.is_numeric_dtype(df[col]):
                max_val = df[col].max()
                max_row = df[df[col] == max_val]
                return f"Maximum {col}: {max_val}, found in row: {max_row.to_dict('records')[0]}"
                
    elif "count" in query:
        if "group by" in query or "grouped by" in query:
            for col in df.columns:
                if col.lower() in query:
                    return f"Count by {col}:\n{df[col].value_counts()}"
        else:
            return f"Total count of rows: {len(df)}"
    
    # Return a generic response if no specific analysis was matched
    return "I couldn't process that query. Here's some basic information about your data:\n" + \
           f"- Number of rows: {len(df)}\n" + \
           f"- Columns: {', '.join(df.columns)}\n" + \
           f"- Data types: {df.dtypes.to_string()}"

# Add this to the sidebar section of your dashboard
with st.sidebar:
    st.header("Chat with Your Data")

    if PANDAS_AI_AVAILABLE:
        # Load data for chat
        df_data = load_data()  # Your existing load_data function
        
        if not df_data.empty:
            # Add diagnostics section
            with st.expander("Diagnostics", expanded=False):
                st.write("Data Preview:")
                st.dataframe(df_data.head(3))
                
                st.write("Data Types:")
                st.write(df_data.dtypes)
                
                st.write("PandasAI Status:")
                st.write(f"API Key Set: {'Yes' if PANDABI_API_KEY else 'No'}")
                
                # Test API connection
                if st.button("Test API Connection"):
                    try:
                        # Save a tiny test dataset
                        test_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
                        test_df.to_csv("test_data.csv", index=False)
                        
                        # Try to use PandasAI with simple query
                        test_pai_df = pai.read_csv("test_data.csv")
                        with st.spinner("Testing API..."):
                            response = test_pai_df.chat("How many rows are in this data?")
                            st.success(f"Connection successful! Response: {response}")
                    except Exception as e:
                        st.error(f"API Connection failed: {str(e)}")
            
            # Initialize chat history if it doesn't exist
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []

            # Create the chat input
            user_query = st.text_input(
                "Ask a question about your data:",
                placeholder="e.g., What is the total profit by country?"
            )

            # Fallback option toggle
            use_fallback = st.checkbox("Use pandas fallback if PandasAI fails", value=True)

            if user_query:
                with st.spinner("Analyzing your data..."):
                    try:
                        # First attempt: Save to CSV and use PandasAI
                        temp_csv = "temp_data_for_pai.csv"
                        df_data.to_csv(temp_csv, index=False)
                        
                        # Use PandasAI
                        pai_df = pai.read_csv(temp_csv)
                        
                        # Try multiple times with increasing timeout
                        max_attempts = 3
                        for attempt in range(1, max_attempts + 1):
                            try:
                                with st.spinner(f"Attempt {attempt}/{max_attempts} - Analyzing data..."):
                                    # Set a timeout for the API call
                                    response = pai_df.chat(user_query)
                                    
                                    # Check if we got a valid response
                                    if "not able to get your answer" in response or not response:
                                        if attempt < max_attempts:
                                            st.warning(f"Retrying... (attempt {attempt}/{max_attempts})")
                                            time.sleep(2)  # Wait before retrying
                                            continue
                                        else:
                                            raise Exception("PandasAI couldn't process the query")
                                    
                                    # Success path
                                    st.success("Analysis complete!")
                                    st.markdown(f"**Answer:** {response}")
                                    
                                    # Add to chat history
                                    st.session_state.chat_history.append({
                                        "query": user_query,
                                        "response": response,
                                        "method": "PandasAI"
                                    })
                                    break  # Exit the retry loop on success
                                    
                            except Exception as e:
                                if attempt < max_attempts:
                                    st.warning(f"Attempt failed. Retrying... ({attempt}/{max_attempts})")
                                    time.sleep(2)  # Wait before retrying
                                else:
                                    raise e  # Re-raise the exception after all attempts
                        
                    except Exception as e:
                        st.error(f"PandasAI analysis failed: {str(e)}")
                        
                        # Use fallback analysis with pandas if enabled
                        if use_fallback:
                            st.warning("Switching to pandas fallback analysis...")
                            fallback_response = fallback_analysis(df_data, user_query)
                            st.markdown(f"**Fallback Answer:** {fallback_response}")
                            
                            # Add to chat history
                            st.session_state.chat_history.append({
                                "query": user_query,
                                "response": fallback_response,
                                "method": "Pandas Fallback"
                            })
                        else:
                            st.info("Try rephrasing your question or enabling the fallback option.")

            # Display chat history
            if st.session_state.chat_history:
                st.subheader("Chat History")
                for i, chat in enumerate(reversed(st.session_state.chat_history)):
                    with st.expander(f"Q: {chat['query'][:50]}..." if len(chat['query']) > 50 else f"Q: {chat['query']}"):
                        st.markdown("**Question:**")
                        st.info(chat['query'])
                        st.markdown(f"**Answer:** ({chat['method']})")
                        st.success(chat['response'])

                # Clear chat history button
                if st.button("Clear Chat History"):
                    st.session_state.chat_history = []
                    st.experimental_rerun()
                    
            # Add example questions to help users
            with st.expander("Recommended Questions"):
                st.markdown("""
                Try these questions that have been tested to work:
                - How many rows are in this dataset?
                - What are the column names?
                - What is the maximum profit?
                - What is the minimum sales?
                - Count the rows by country
                - Calculate the average sales
                """)
        else:
            st.warning(
                "No data available for analysis. Please check your data.csv file."
            )
    else:
        # Handle case where PandaBI setup is not complete
        if not PANDABI_API_KEY:
            api_key = st.text_input("Enter your PandaBI API key:", type="password")
            if api_key and st.button("Save API Key"):
                try:
                    pai.api_key.set(api_key)
                    st.success("API key set successfully! Refreshing...")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error setting API key: {str(e)}")
        else:
            st.warning("""
            PandasAI package is not available. To enable the chat feature, please install the required package:
            ```
            pip install pandasai
            ```
            Then restart the application.
            """)