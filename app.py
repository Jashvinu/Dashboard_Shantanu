import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

try:
    import pandasai as pai
    from pandasai_openai import OpenAI
    
    # Load OpenAI LLM
    llm = OpenAI(
    api_token=st.secrets["OPENAI_API_KEY"],
    model="gpt-4o-mini",      # Choose model: gpt-4, gpt-3.5-turbo, etc.
    temperature=0.2,            # 0.0 (deterministic) to 1.0 (creative)
    max_tokens=4000,            # Maximum length of response
    additional_kwargs={          # Optional additional parameters
        "top_p": 0.95,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }
)
    
    # Configure OpenAI LLM in PandasAI
    pai.config.set({
        "llm": llm,
    })
    
    PANDAS_AI_AVAILABLE = True
    
except ImportError:
    PANDAS_AI_AVAILABLE = False
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
with st.sidebar:
    st.header("Chat with Your Data")
    
    if PANDAS_AI_AVAILABLE:
        # Display LLM configuration information (optional, can be toggled)
        with st.expander("LLM Configuration"):
            st.write(f"LLM Type: {type(llm).__name__}")
            st.write("LLM Configuration:")
            st.write(f"- Model: {llm.model}")
            st.write(f"- Temperature: {llm.temperature}")
            st.write(f"- Max Tokens: {llm.max_tokens}")
            
            # Verify LLM configuration
            config = pai.config.get()
            st.write(f"- LLM in config: {type(config.llm).__name__}")
        
        # Load data
        @st.cache_data
        def load_data_for_chat():
            try:
                # Read the data.csv file as specified
                return pai.read_csv("data.csv")
            except Exception as e:
                st.error(f"Error reading data.csv: {str(e)}")
                return None
        
        df = load_data_for_chat()
        
        if df is not None:
            try:
                # Initialize chat history if it doesn't exist
                if 'chat_history' not in st.session_state:
                    st.session_state.chat_history = []
                
                # Create the chat input with a more descriptive prompt
                user_query = st.text_input(
                    "Ask a question about your data (e.g., 'What is the correlation between Sales and Profit?'):"
                )
                
                if user_query:
                    with st.spinner("Analyzing your data..."):
                        try:
                            # Use direct chat method with PandasAI
                            response = df.chat(user_query)
                            
                            # Add to chat history
                            st.session_state.chat_history.append({
                                "query": user_query,
                                "response": response
                            })
                            
                            # Display the response in a success box
                            st.success("Analysis complete!")
                            st.markdown(f"### Answer:\n{response}")
                            
                        except Exception as e:
                            st.error(f"Error analyzing data: {str(e)}")
                
                # Display chat history with better formatting
                if st.session_state.chat_history:
                    st.subheader("Chat History")
                    for i, chat in enumerate(reversed(st.session_state.chat_history)):
                        with st.expander(f"Q: {chat['query'][:50]}..." if len(chat['query']) > 50 else f"Q: {chat['query']}"):
                            st.markdown("**Question:**")
                            st.info(chat['query'])
                            st.markdown("**Answer:**")
                            st.success(chat['response'])
                    
                    # Clear chat history button
                    if st.button("Clear Chat History"):
                        st.session_state.chat_history = []
                        st.experimental_rerun()
                        
                # Add example questions to help users
                with st.expander("Example Questions"):
                    st.markdown("""
                    Try asking:
                    - What is the total profit by country?
                    - Which product has the highest sales?
                    - Show me the trend of units sold over time
                    - Compare performance between segments
                    - What's the correlation between discount and profit?
                    """)
                    
            except Exception as e:
                st.error(f"Error initializing chat: {str(e)}")
        else:
            st.warning(
                "No data available for analysis. Please ensure data.csv exists and is properly formatted."
            )
    else:
        st.warning("""
        PandasAI package is not available. To enable the chat feature, please install the required packages:
        ```
        pip install pandasai pandasai-openai
        ```
        Then restart the application.
        """)
        
        # Alternative visualization options
        st.subheader("Alternative Data Exploration")
        
        # Add options to view basic stats about the data
        if st.button("View Data Summary"):
            df = pd.read_csv("data.csv")
            if not df.empty:
                st.write("Data Shape:", df.shape)
                st.write("Column Types:")
                st.write(df.dtypes)
                st.write("Basic Statistics:")
                st.write(df.describe())