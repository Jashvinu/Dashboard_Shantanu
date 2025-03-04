import streamlit as st
import pandas as pd
from utils.pandasai_config import PANDAS_AI_AVAILABLE
import io
from PIL import Image
import matplotlib.pyplot as plt
import uuid

@st.cache_data
def load_data():
    """Load data from CSV file and preprocess it"""
    try:
        # Read the CSV file directly
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

# Custom chart function to keep charts in memory
def in_memory_chart_function(chart):
    """Store chart in session state and return a reference"""
    # Generate a unique identifier for the chart
    chart_id = f"chart_{uuid.uuid4()}"
    
    # Convert matplotlib figure to bytes
    buffer = io.BytesIO()
    chart.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Store in session state
    if 'memory_images' not in st.session_state:
        st.session_state.memory_images = {}
    st.session_state.memory_images[chart_id] = buffer
    
    # Return reference to the chart
    return chart_id

def load_data_for_chat():
    """Load data for the chat functionality using PandasAI"""
    try:
        if PANDAS_AI_AVAILABLE:
            import pandasai as pai
            
            # Read the data file
            df = pd.read_csv("data.csv")
            
            # Create a SmartDataframe with our custom configuration
            smart_df = pai.SmartDataframe(df, config={"custom_chart_function": in_memory_chart_function})
            
            return smart_df
        else:
            return None
    except Exception as e:
        st.error(f"Error reading data.csv for chat: {str(e)}")
        return None