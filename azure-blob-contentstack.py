import streamlit as st
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError
from contentstack import Client
import os
import json

# Azure Blob Storage configurations
STORAGE_ACCOUNT_NAME = 'your_storage_account_name'
STORAGE_ACCOUNT_KEY = 'your_storage_account_key'
CONTAINER_NAME = 'your_container_name'

# ContentStack configurations
CONTENTSTACK_API_KEY = 'your_contentstack_api_key'
CONTENTSTACK_DELIVERY_TOKEN = 'your_contentstack_delivery_token'
CONTENTSTACK_ENVIRONMENT = 'your_contentstack_environment'

# Function to upload file to Azure Blob Storage
def upload_to_azure(file_name, file_content, container_name):
    try:
        # Create a blob service client
        blob_service_client = BlobServiceClient(account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net", credential=STORAGE_ACCOUNT_KEY)
        
        # Create a container if it does not exist
        try:
            container_client = blob_service_client.create_container(container_name)
            st.success(f"Container '{container_name}' created.")
        except ResourceExistsError:
            container_client = blob_service_client.get_container_client(container_name)
            st.info(f"Container '{container_name}' already exists.")
        
        # Create a blob client
        blob_client = container_client.get_blob_client(file_name)
        
        # Upload file to Azure Blob Storage
        blob_client.upload_blob(file_content, overwrite=True)
        st.success(f"File '{file_name}' uploaded successfully to container '{container_name}'.")
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Function to download entries from ContentStack
def download_entries(content_type_uid):
    try:
        client = Client(api_key=CONTENTSTACK_API_KEY, delivery_token=CONTENTSTACK_DELIVERY_TOKEN, environment=CONTENTSTACK_ENVIRONMENT)
        entries = client.content_type(content_type_uid).entries().find()
        return entries
    except Exception as e:
        st.error(f"An error occurred while fetching entries: {str(e)}")
        return None

# Streamlit web interface
st.title("ContentStack to Azure Blob Storage")

# Content type input
content_type_uid = st.text_input("Enter Content Type UID")

# Container name input
container_name = st.text_input("Enter Azure Blob Storage Container Name", CONTAINER_NAME)

# Download and upload entries
if st.button("Download and Upload Entries"):
    if content_type_uid:
        entries = download_entries(content_type_uid)
        if entries:
            st.write("Entries downloaded successfully.")
            for entry in entries:
                file_name = f"{content_type_uid}_{entry['uid']}.json"
                file_content = json.dumps(entry).encode('utf-8')
                upload_to_azure(file_name, file_content, container_name)
    else:
        st.error("Please enter a valid Content Type UID.")
