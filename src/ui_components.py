import streamlit as st
from document_processing import upload_pdf,get_related_documents
from chat_logic import process_pdf_chat, process_selected_documents_chat,process_continue_generate


def initialize_session_state():
    defaults = {
        'messages': [{"role": "assistant", "content": "Can I assist you today?"}],
        'related_document': None,
        'selected_document': [],
        'document_chat': None,
        'number': 3,
        'prompt': None,
        'uploaded_file': None,
        'current_file': None,
        'clear_chat': False,
        'generate_clicked': False,
        'last_assistant_index': 0 
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def display_sidebar():
    with st.sidebar:
        st.title("FIND RELATED RESEARCH📄")
        text_input = st.text_input("Enter your undergraduate thesis Title 👇")
        
        new_number = st.number_input('Insert a min number of the research', min_value=1, format='%i', value=st.session_state['number'])
        
        if new_number != st.session_state['number']:
            st.session_state['number'] = new_number
            if st.session_state.get('prompt'):
                st.session_state['related_document'] = get_related_documents(st.session_state['prompt'])
                st.session_state['selected_document'] = []  # Reset selected documents
        
        if text_input and (st.session_state.get('prompt') != text_input or 'related_document' not in st.session_state):
            st.session_state['prompt'] = text_input
            st.session_state['related_document'] = get_related_documents(text_input)
            st.session_state['selected_document'] = []  # Reset selected documents

        display_retrieved_documents()

    return text_input

def display_retrieved_documents():
    if st.session_state.get('related_document'):
        st.subheader("Retrieved Documents")
        for i, doc in enumerate(st.session_state['related_document']['related_documents']):
            st.markdown(f"**Document {i+1}**")
            st.markdown(f"**Judul**: {doc['judul']}")
            st.markdown(f"**URL**: [{doc['url']}]({doc['url']})")
            
            if st.session_state['uploaded_file'] is None:
                if st.checkbox(f"Select Document {i+1}", key=f"checkbox_{i}"):
                    if doc not in st.session_state['selected_document']:
                        st.session_state['selected_document'].append(doc)
                else:
                    if doc in st.session_state['selected_document']:
                        st.session_state['selected_document'].remove(doc)
            else:
                st.warning('Clear the PDF first before selecting Document')
            
            st.markdown("---")

def display_chat_interface():
    if 'continued_messages' not in st.session_state:
        st.session_state.continued_messages = set()

    if st.button("Clear Chat", key="clear_chat_button"):
        st.session_state.clear_chat = True
        st.session_state.messages = [{"role": "assistant", "content": "Chat cleared. How can I assist you?"}]
        st.session_state.continued_messages = set()

    if not st.session_state['selected_document']:
        st.session_state['uploaded_file'] = st.file_uploader("Choose a PDF")
    
    if st.session_state.get('current_file') != st.session_state['uploaded_file']:
        if st.session_state['uploaded_file']:
            with st.spinner("Processing uploaded PDF. Please wait..."):
                upload_pdf(st.session_state['uploaded_file'])
            st.session_state['current_file'] = st.session_state['uploaded_file']
            st.success("PDF processed successfully!")

    chat_enabled = st.session_state['uploaded_file'] is not None or st.session_state['selected_document']

    if chat_enabled:
        if prompt := st.chat_input("Type your message here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            generate_response(prompt)
    
    for i in range(len(st.session_state.messages)):
        message = st.session_state.messages[i]
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
        
        # Add Generate More button after each assistant message, except the initial greeting
        if message["role"] == "assistant" and i > 0 and i not in st.session_state.continued_messages:
            if st.button("Continue Generate", key=f"generate_more_{i}"):
                new_response = continue_generation(i)
                if new_response:
                    st.session_state.messages.append({"role": "assistant", "content": new_response})
                    st.session_state.continued_messages.add(i)
                    st.rerun()

    if st.session_state['uploaded_file']:
        st.info("You are currently chatting with the uploaded PDF.")
    elif st.session_state['selected_document']:
        st.info("You are currently chatting with the selected documents from the search results.")


def continue_generation(index):
    last_user_message = next((msg["content"] for msg in reversed(st.session_state.messages[:index]) if msg["role"] == "user"), None)
    if last_user_message:
        previous_response = st.session_state.messages[index]["content"]
        
        if st.session_state['uploaded_file']:
            context = "PDF content"  # You might want to adjust this based on how you're handling PDF content
        elif st.session_state['selected_document']:
            context = "\n\n".join(f"{doc['judul']} {doc['abstrak']} {doc['url']}" for doc in st.session_state['selected_document'])
        else:
            context = ""

        with st.spinner("Generating more..."):
            new_response = process_continue_generate(last_user_message, previous_response, context)

        return new_response
    return None


def generate_response(prompt, is_continuation=False):
    with st.spinner("Thinking..."):
        if st.session_state['uploaded_file']:
            previous_response = st.session_state.messages[-1]["content"] if is_continuation else ""
            response = process_pdf_chat(prompt, previous_response)
        elif st.session_state['selected_document']:
            previous_response = st.session_state.messages[-1]["content"] if is_continuation else ""
            response = process_selected_documents_chat(prompt, previous_response)
        
        if not is_continuation:
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        return response