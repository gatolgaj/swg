import os
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Qdrant
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()

# Load environment variables
load_dotenv()
# name = f"projects/236909908642/secrets/open-ai-api-key/versions/1"
# response = client.access_secret_version(request={"name": name})
# OPENAI_API_KEY =response.payload.data.decode("UTF-8")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')

# Initialize OpenAI Embeddings
embeddings_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

# Function to process and store files in Qdrant
def process_and_store_files(folder_path):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            loader = PyPDFLoader(file_path)
            #  document = loader.load()
            docs =  loader.load_and_split() #text_splitter.split_documents(document)

            # Determine the collection based on filename
            collection_name = "Candidates" if filename.startswith("candidate-") else "Documents"

            # Store in Qdrant using the embeddings model
            qdrant = Qdrant.from_documents(
                docs,
                embeddings_model,
                url=QDRANT_URL,
                prefer_grpc=True,
                collection_name=collection_name
            )

# Specify the folder containing the files
folder_path = 'pdfInput'
process_and_store_files(folder_path)

print("Files processed and stored in Qdrant.")
