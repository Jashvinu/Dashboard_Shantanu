import streamlit as st
from utils.data_loader import load_data_for_chat, in_memory_chart_function
from utils.pandasai_config import PANDAS_AI_AVAILABLE, display_in_memory_image
import re
import os

def render_chat_component():
    """Render a standalone chat component that displays responses directly below"""
    st.header("Chat with Your Data")

    # Initialize image gallery state if needed
    if 'image_gallery' not in st.session_state:
        st.session_state.image_gallery = []

    if PANDAS_AI_AVAILABLE:
        try:
            # Load data
            df = load_data_for_chat()

            if df is not None:
                # Initialize chat history if it doesn't exist
                if 'chat_history' not in st.session_state:
                    st.session_state.chat_history = []

                # Use a form with a unique key
                with st.form(key="chat_form"):
                    user_query = st.text_input(
                        "Ask a question about your data:",
                        placeholder="E.g., Show loan data by chart"
                    )
                    submit_button = st.form_submit_button("Analyze Data")
                
                    if submit_button and user_query:
                        # Set a flag to process after the form is submitted
                        st.session_state.process_query = True
                        st.session_state.current_query = user_query

                # Process the query outside the form if flag is set
                if 'process_query' in st.session_state and st.session_state.process_query:
                    with st.spinner("Analyzing your data..."):
                        try:
                            response = df.chat(st.session_state.current_query)
                            
                            # Process the response for image detection
                            image_path = None
                            if isinstance(response, str):
                                # Check for chart ID
                                if response.startswith("chart_"):
                                    image_path = response.strip()
                                # Check for file path
                                elif response.startswith("exports/") and (
                                    response.endswith(".png") or 
                                    response.endswith(".jpg") or
                                    response.endswith(".jpeg")
                                ):
                                    image_path = response.strip()
                            
                            # Add to gallery if it's an image
                            if image_path is not None:
                                st.session_state.image_gallery.append({
                                    "id": len(st.session_state.image_gallery),
                                    "path": image_path,
                                    "query": st.session_state.current_query,
                                    "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                            
                            # Store in chat history
                            st.session_state.chat_history.append({
                                "query": st.session_state.current_query,
                                "response": response
                            })
                            
                            # Reset the flag to prevent infinite loop
                            st.session_state.process_query = False
                        except Exception as e:
                            st.error(f"Error analyzing data: {str(e)}")
                            # Reset the flag to prevent infinite loop
                            st.session_state.process_query = False
                            
                # Display current analysis result (if available)
                if 'chat_history' in st.session_state and st.session_state.chat_history:
                    latest_query = st.session_state.chat_history[-1]["query"]
                    latest_response = st.session_state.chat_history[-1]["response"]
                    
                    # Show success message
                    st.success("Analysis complete!")
                    
                    # Display the response
                    if isinstance(latest_response, str):
                        # Check if response is just a chart_id (in-memory chart)
                        if latest_response.startswith("chart_"):
                            chart_id = latest_response.strip()
                            # Try to display the in-memory image
                            if not display_in_memory_image(chart_id):
                                st.warning("Could not display the generated chart.")
                                st.text(latest_response)
                        # Check if it's a file path (for backward compatibility)
                        elif latest_response.startswith("exports/") and (
                            latest_response.endswith(".png") or 
                            latest_response.endswith(".jpg")
                        ):
                            # Try to display it if it exists
                            if os.path.exists(latest_response):
                                st.image(latest_response)
                            else:
                                st.text("Chart generated with file path: " + latest_response)
                        else:
                            # Regular text response
                            st.markdown(latest_response)
                    else:
                        # For non-string responses (could be pandas dataframes, plotly figures, etc.)
                        st.write(latest_response)

                # Display the image gallery if we have images
                if st.session_state.image_gallery:
                    st.subheader("Image Gallery")
                    
                    # Create a horizontal layout for image selector
                    gallery_cols = st.columns([1, 3])
                    
                    with gallery_cols[0]:
                        # Create a selectbox for image selection
                        image_options = [f"#{img['id']}: {img['query'][:20]}..." for img in st.session_state.image_gallery]
                        selected_idx = st.selectbox("Select image:", 
                                                   range(len(image_options)), 
                                                   format_func=lambda i: image_options[i])
                        
                        # Button to clear gallery
                        if st.button("Clear Gallery"):
                            st.session_state.image_gallery = []
                            st.rerun()
                    
                    with gallery_cols[1]:
                        # Display the selected image
                        if selected_idx is not None and selected_idx < len(st.session_state.image_gallery):
                            img_data = st.session_state.image_gallery[selected_idx]
                            
                            # Display image details
                            st.markdown(f"**Query:** {img_data['query']}")
                            st.markdown(f"**Created:** {img_data['timestamp']}")
                            
                            # Display the image
                            img_path = img_data['path']
                            if img_path.startswith("chart_"):
                                display_in_memory_image(img_path)
                            elif os.path.exists(img_path):
                                st.image(img_path)
                            else:
                                st.warning(f"Image not found: {img_path}")

                # Example Questions expandable section
                with st.expander("Example Questions"):
                    st.markdown("""
                    Try asking:
                    - What is the total profit by country?
                    - Show loan data by chart
                    - Types of loans
                    - Show a pie chart based on education
                    - Compare performance between segments
                    """)
                
                # Display previous analyses
                if len(st.session_state.chat_history) > 0:
                    st.subheader("Previous Analyses")
                    
                    # Clear history button
                    if st.button("Clear History"):
                        st.session_state.chat_history = []
                        st.rerun()
                    
                    # Show all except the most recent (which is already shown above)
                    for i, chat in enumerate(reversed(st.session_state.chat_history[:-1])):
                        with st.expander(f"Q: {chat['query']}"):
                            st.markdown("**Question:**")
                            st.info(chat['query'])
                            st.markdown("**Answer:**")
                            
                            # For text responses, just show the text
                            if isinstance(chat['response'], str) and not (
                                chat['response'].startswith("chart_") or 
                                (chat['response'].startswith("exports/") and 
                                 (chat['response'].endswith(".png") or chat['response'].endswith(".jpg")))
                            ):
                                st.markdown(chat['response'])
                            elif isinstance(chat['response'], str):
                                st.text("Response included a chart. See Image Gallery.")
                            else:
                                # For non-string responses
                                st.write(chat['response'])

            else:
                st.warning(
                    "No data available for analysis. Please ensure data.csv exists and is properly formatted."
                )
        except Exception as e:
            st.error(f"Error initializing chat: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
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
            try:
                import pandas as pd
                df = pd.read_csv("data.csv")
                if not df.empty:
                    st.write("Data Shape:", df.shape)
                    st.write("Column Types:")
                    st.write(df.dtypes)
                    st.write("Basic Statistics:")
                    st.write(df.describe())
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")