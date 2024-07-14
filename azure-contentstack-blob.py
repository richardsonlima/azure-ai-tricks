import streamlit as st
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError
from contentstack import Client
import os
import json
from azure.ai.openai import OpenAIClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchFieldDataType

# Azure configurations
STORAGE_ACCOUNT_NAME = 'your_storage_account_name'
STORAGE_ACCOUNT_KEY = 'your_storage_account_key'
CONTAINER_NAME = 'your_container_name'

CONTENTSTACK_API_KEY = 'your_contentstack_api_key'
CONTENTSTACK_DELIVERY_TOKEN = 'your_contentstack_delivery_token'
CONTENTSTACK_ENVIRONMENT = 'your_contentstack_environment'

OPENAI_API_KEY = 'your_openai_api_key'
SEARCH_SERVICE_ENDPOINT = 'your_search_service_endpoint'
SEARCH_ADMIN_API_KEY = 'your_search_admin_api_key'

# Function to upload file to Azure Blob Storage
def upload_to_azure(file_name, file_content, container_name):
    try:
        blob_service_client = BlobServiceClient(account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net", credential=STORAGE_ACCOUNT_KEY)
        try:
            container_client = blob_service_client.create_container(container_name)
            st.success(f"Container '{container_name}' created.")
        except ResourceExistsError:
            container_client = blob_service_client.get_container_client(container_name)
            st.info(f"Container '{container_name}' already exists.")
        blob_client = container_client.get_blob_client(file_name)
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

# Function to generate embeddings
def generate_embeddings(text, embedding_model_name):
    openai_client = OpenAIClient(endpoint=f"https://{embedding_model_name}.openai.azure.com/", credential=AzureKeyCredential(OPENAI_API_KEY))
    response = openai_client.embeddings(content=text)
    return response['data'][0]['embedding']

# Function to create Azure AI Search index
def create_search_index(index_name, json_fields):
    search_index_client = SearchIndexClient(endpoint=SEARCH_SERVICE_ENDPOINT, credential=AzureKeyCredential(SEARCH_ADMIN_API_KEY))
    fields = [SimpleField(name=field, type=SearchFieldDataType.String, filterable=True, sortable=True, searchable=True) for field in json_fields]
    index = SearchIndex(name=index_name, fields=fields)
    search_index_client.create_index(index)

# Function to upload documents to Azure AI Search
def upload_documents_to_search(index_name, documents):
    search_client = SearchClient(endpoint=SEARCH_SERVICE_ENDPOINT, index_name=index_name, credential=AzureKeyCredential(SEARCH_ADMIN_API_KEY))
    search_client.upload_documents(documents)

# Streamlit web interface
st.title("ContentStack to Azure Blob Storage and AI Search")

content_type_uid = st.text_input("Enter Content Type UID")
container_name = st.text_input("Enter Azure Blob Storage Container Name", CONTAINER_NAME)
embedding_model_name = st.text_input("Enter Embedding Model Name")
index_name = st.text_input("Enter Azure AI Search Index Name")
json_fields = st.text_input("Enter JSON Fields for Index (comma-separated)").split(',')

if st.button("Download, Process, and Upload"):
    if content_type_uid and embedding_model_name and index_name and json_fields:
        entries = download_entries(content_type_uid)
        if entries:
            st.write("Entries downloaded successfully.")
            create_search_index(index_name, json_fields)
            documents = []
            for entry in entries:
                document = {field: entry.get(field, '') for field in json_fields}
                document['embedding'] = generate_embeddings(json.dumps(document), embedding_model_name)
                documents.append(document)
                file_name = f"{content_type_uid}_{entry['uid']}.json"
                file_content = json.dumps(entry).encode('utf-8')
                upload_to_azure(file_name, file_content, container_name)
            upload_documents_to_search(index_name, documents)
            st.success("Entries processed and uploaded to Azure Blob Storage and AI Search.")
    else:
        st.error("Please fill in all fields.")
