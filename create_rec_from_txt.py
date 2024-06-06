import os
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Qdrant

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

# Initialize OpenAI Embeddings
embeddings_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

# Function to process and store files in Qdrant
def process_and_store_files(folder_path):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            loader = TextLoader(file_path)
            document = loader.load()
            docs = text_splitter.split_documents(document)

            # Determine the collection based on filename
            collection_name = "Candidates" if filename.startswith("candidate-") else "Patients"

            # Store in Qdrant using the embeddings model
            qdrant = Qdrant.from_documents(
                docs,
                embeddings_model,
                url=QDRANT_URL,
                port=6334,
                prefer_grpc=True,
                collection_name=collection_name
            )

# Specify the folder containing the files
folder_path = 'Pdata'
process_and_store_files(folder_path)

print("Files processed and stored in Qdrant.")
