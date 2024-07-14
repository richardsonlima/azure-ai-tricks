import streamlit as st
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError
import os

# pip3 install azure-storage-blob
# streamlit run app.py 

# Azure Blob Storage configurations
STORAGE_ACCOUNT_NAME = 'your_storage_account_name'
STORAGE_ACCOUNT_KEY = 'your_storage_account_key'
CONTAINER_NAME = 'your_container_name'

# Function to upload file to Azure Blob Storage
def upload_to_azure(file, container_name):
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
        blob_client = container_client.get_blob_client(file.name)
        
        # Upload file to Azure Blob Storage
        blob_client.upload_blob(file, overwrite=True)
        st.success(f"File '{file.name}' uploaded successfully to container '{container_name}'.")
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Streamlit web interface
st.title("Azure Blob Storage File Upload")

uploaded_file = st.file_uploader("Choose a file", type=["jpg", "png", "jpeg", "pdf", "txt", "csv", "json", "parquet"])

if uploaded_file is not None:
    st.write("File upload initiated...")
    upload_to_azure(uploaded_file, CONTAINER_NAME)
