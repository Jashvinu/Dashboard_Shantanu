import streamlit as st
from utils.page_config import setup_page_config, init_session_state, apply_custom_css
from components.header import render_header
from components.project_tab import render_project_tab
from components.finance_tab import render_finance_tab
from components.data_tab import render_data_tab
from components.chat import render_chat_component

def main():
    # Setup page configuration
    setup_page_config()
    init_session_state()
    apply_custom_css()
    
    # Render header
    render_header()
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Project Management", "Finance & Reports", "Data Table", "Chat with Data"])
    
    with tab1:
        render_project_tab()
    
    with tab2:
        render_finance_tab()
    
    with tab3:
        render_data_tab()
        
    with tab4:
        # Add the chat component directly as a tab
        render_chat_component()

if __name__ == "__main__":
    main()