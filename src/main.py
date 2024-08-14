import streamlit as st
from ui_components import initialize_session_state, display_sidebar, display_chat_interface

def main():
    st.title("💬 IPB-GPT")
    st.caption("🚀 A Repository Chatbot that helps you find related research about your undergraduate thesis")

    initialize_session_state()
    display_sidebar()
    display_chat_interface()

if __name__ == "__main__":
    main()