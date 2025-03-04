import streamlit as st
import io
from PIL import Image
import base64
import matplotlib.pyplot as plt
import os
import uuid

# Initialize session state for storing images
if 'memory_images' not in st.session_state:
    st.session_state.memory_images = {}

# Custom chart handling function that prevents popups
def custom_chart_function(chart):
    """Store chart in session state and prevent direct display"""
    # Generate a unique identifier for the chart
    chart_id = f"chart_{uuid.uuid4()}"
    
    # Convert matplotlib figure to bytes
    buffer = io.BytesIO()
    chart.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Store in session state
    st.session_state.memory_images[chart_id] = buffer
    
    # Important: Close the figure to prevent display
    plt.close(chart)
    
    # Return reference to the chart
    return chart_id

# Helper function to display image from memory
def display_in_memory_image(chart_id):
    if chart_id in st.session_state.memory_images:
        image_bytes = st.session_state.memory_images[chart_id]
        # Reset buffer position
        image_bytes.seek(0)
        # Open and display the image
        image = Image.open(image_bytes)
        st.image(image)
        return True
    return False

# Initialize PandasAI with OpenAI integration if available
try:
    import pandasai as pai
    from pandasai_openai import OpenAI
    
    # Load OpenAI LLM
    llm = OpenAI(
        api_token=st.secrets["OPENAI_API_KEY"],
        model="gpt-4o-mini",
        temperature=0.2,
        max_tokens=4000,
        additional_kwargs={
            "top_p": 0.95,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
    )
    
    # Set the LLM in PandasAI config
    pai.config.llm = llm
    
    # Disable saving charts to files - This is crucial
    pai.config.save_charts = False
    
    # Set our custom chart function
    pai.config.custom_chart_function = custom_chart_function
    
    # Ensure charts don't open directly
    pai.config.open_charts = False
    
    # Disable any display hooks
    pai.config.enable_cache = False
    
    PANDAS_AI_AVAILABLE = True

except ImportError:
    PANDAS_AI_AVAILABLE = False
