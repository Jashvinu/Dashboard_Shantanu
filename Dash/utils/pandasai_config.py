import streamlit as st
import io
from PIL import Image
import base64

# Initialize session state for storing images
if 'memory_images' not in st.session_state:
    st.session_state.memory_images = {}

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

    PANDAS_AI_AVAILABLE = True

except ImportError:
    PANDAS_AI_AVAILABLE = False