import streamlit as st
from contentstack import Client
import json

# ContentStack configurations
CONTENTSTACK_API_KEY = 'your_contentstack_api_key'
CONTENTSTACK_DELIVERY_TOKEN = 'your_contentstack_delivery_token'
CONTENTSTACK_ENVIRONMENT = 'your_contentstack_environment'
CONTENTSTACK_MANAGEMENT_TOKEN = 'your_contentstack_management_token'

# Function to create a ContentStack entry
def create_contentstack_entry(stack_name, content_type_name, entry_data):
    try:
        client = Client(api_key=CONTENTSTACK_API_KEY, delivery_token=CONTENTSTACK_DELIVERY_TOKEN, environment=CONTENTSTACK_ENVIRONMENT)
        stack = client.stack(api_key=stack_name, management_token=CONTENTSTACK_MANAGEMENT_TOKEN)
        content_type = stack.content_type(content_type_name)
        entry = content_type.entry()
        entry.update(entry_data)
        entry.save()
        st.success(f"Entry created successfully in stack '{stack_name}' and content type '{content_type_name}'.")
    except Exception as e:
        st.error(f"An error occurred while creating the entry: {str(e)}")

# Streamlit web interface
st.title("LLM Knowledge Base and ContentStack Entry")

# User inputs
stack_name = st.text_input("Enter ContentStack Stack Name")
content_type_name = st.text_input("Enter Content Type Name")
knowledge_base = st.text_area("Enter Knowledge Base Content")

if st.button("Create Knowledge Base and ContentStack Entry"):
    if stack_name and content_type_name and knowledge_base:
        # Create a knowledge base entry
        entry_data = {
            "title": "LLM Knowledge Base Entry",
            "content": knowledge_base
        }
        # Create ContentStack entry
        create_contentstack_entry(stack_name, content_type_name, entry_data)
    else:
        st.error("Please fill in all fields.")
