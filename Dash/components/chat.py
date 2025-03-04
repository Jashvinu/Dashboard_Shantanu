import streamlit as st
from utils.data_loader import load_data_for_chat
from utils.pandasai_config import PANDAS_AI_AVAILABLE, display_in_memory_image
import re
import os
import pandas as pd
from datetime import datetime

def render_chat_component():
    """Render a standalone chat component that displays responses directly below"""
    st.header("Chat with Your Data")

    # Initialize chat history if it doesn't exist
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize current image
    if 'current_image' not in st.session_state:
        st.session_state.current_image = None

    if PANDAS_AI_AVAILABLE:
        try:
            # Create tab layout for chat and gallery
            tabs = st.tabs(["Chat", "Image Gallery"])
            
            with tabs[0]:  # Chat tab
                # Load data
                df = load_data_for_chat()

                if df is not None:
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
                                # Get the response
                                response = df.chat(st.session_state.current_query)
                                
                                # Store in chat history
                                st.session_state.chat_history.append({
                                    "query": st.session_state.current_query,
                                    "response": response,
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                                
                                # If it's a chart, update the current image
                                if isinstance(response, str) and response.startswith("chart_"):
                                    st.session_state.current_image = response
                                    # Auto-switch to gallery tab when a chart is generated
                                    st.experimental_set_query_params(active_tab="gallery")
                                
                                # Reset the flag to prevent infinite loop
                                st.session_state.process_query = False
                            except Exception as e:
                                st.error(f"Error analyzing data: {str(e)}")
                                # Reset the flag to prevent infinite loop
                                st.session_state.process_query = False

                    # Display chat history
                    if st.session_state.chat_history:
                        st.subheader("Conversation")
                        
                        # Display each message
                        for i, chat in enumerate(st.session_state.chat_history):
                            # User message
                            with st.container():
                                st.markdown(f"**You:**")
                                st.info(chat["query"])
                            
                            # Assistant message
                            with st.container():
                                st.markdown(f"**Assistant:** _(at {chat.get('timestamp', '')})_")
                                
                                response = chat["response"]
                                if isinstance(response, str) and response.startswith("chart_"):
                                    st.success("I've generated a chart based on your data. View it in the Image Gallery tab.")
                                    # Add a button to view the image
                                    if st.button(f"View Chart", key=f"view_chart_{i}"):
                                        st.session_state.current_image = response
                                        st.experimental_set_query_params(active_tab="gallery")
                                        st.rerun()
                                elif isinstance(response, str):
                                    st.markdown(response)
                                else:
                                    st.write(response)
                            
                            # Add a separator between messages
                            st.markdown("---")
                        
                        # Button to clear conversation
                        if st.button("Clear Conversation"):
                            st.session_state.chat_history = []
                            st.session_state.current_image = None
                            st.rerun()

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
                else:
                    st.warning(
                        "No data available for analysis. Please ensure data.csv exists and is properly formatted."
                    )
            
            with tabs[1]:  # Image Gallery tab
                st.subheader("Image Gallery")
                
                # Get all charts from chat history
                chart_responses = []
                for i, chat in enumerate(st.session_state.chat_history):
                    response = chat["response"]
                    if isinstance(response, str) and response.startswith("chart_"):
                        chart_responses.append({
                            "chart_id": response,
                            "query": chat["query"],
                            "index": i,
                            "timestamp": chat.get("timestamp", "")
                        })
                
                if chart_responses:
                    # Create a selector for the charts
                    chart_options = [f"#{i+1}: {chart['query'][:30]}..." for i, chart in enumerate(chart_responses)]
                    
                    # Find index of current image
                    selected_idx = 0
                    if st.session_state.current_image:
                        for i, chart in enumerate(chart_responses):
                            if chart["chart_id"] == st.session_state.current_image:
                                selected_idx = i
                                break
                    
                    # Use a selectbox to navigate between charts
                    selected_chart_idx = st.selectbox(
                        "Select chart:",
                        range(len(chart_options)),
                        format_func=lambda i: chart_options[i],
                        index=selected_idx
                    )
                    
                    # Display the selected chart
                    selected_chart = chart_responses[selected_chart_idx]
                    
                    # Update current image
                    st.session_state.current_image = selected_chart["chart_id"]
                    
                    # Display chart info
                    st.markdown(f"**Query:** {selected_chart['query']}")
                    st.markdown(f"**Generated at:** {selected_chart['timestamp']}")
                    
                    # Display the chart
                    st.markdown("### Chart:")
                    display_in_memory_image(selected_chart["chart_id"])
                    
                    # Add navigation buttons
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        if selected_chart_idx > 0:
                            if st.button("Previous Chart"):
                                st.session_state.current_image = chart_responses[selected_chart_idx - 1]["chart_id"]
                                st.rerun()
                    
                    with col2:
                        st.markdown(f"Chart {selected_chart_idx + 1} of {len(chart_responses)}")
                    
                    with col3:
                        if selected_chart_idx < len(chart_responses) - 1:
                            if st.button("Next Chart"):
                                st.session_state.current_image = chart_responses[selected_chart_idx + 1]["chart_id"]
                                st.rerun()
                else:
                    st.info("No charts have been generated yet. Ask a question that requires data visualization to see charts here.")
                
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
