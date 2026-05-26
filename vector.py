import json
import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

# Load JSON data
with open("final_upv_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = "./upv_chroma_db"


# Set to True if format was changed
REBUILD_DB = False

if REBUILD_DB and os.path.exists(db_location):

    import shutil

    shutil.rmtree(db_location)

    print("Old ChromaDB deleted.")




raw_documents = []

for index, item in enumerate(data):
    page_content = f"Title: {item.get('title', '')}\nSource URL: {item.get('url', '')}\nContent: {item.get('content', '')}"
        
    metadata = {
        "title": item.get("title", ""),
        "source": item.get("url", ""),
        "url": item.get("url", ""),
        "type": item.get("type", "general")
    }
    raw_documents.append(Document(page_content=page_content, metadata=metadata))

# Split large documents into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,       
    chunk_overlap=150, 
    separators=["\n\n", "\n", ".", " ", ""]
)
documents = text_splitter.split_documents(raw_documents)
    
# CreateIDs for every chunk
ids = [str(i) for i in range(len(documents))]

add_documents = not os.path.exists(db_location)

vector_store = Chroma(collection_name="upv_website_data", embedding_function=embeddings, persist_directory=db_location)

# Initialize ChromaDB
if add_documents:

    print(f"Embedding {len(documents)} text chunks into ChromaDB. This might take a moment...")
    vector_store.add_documents(documents=documents, ids=ids)
    print("Embedding complete!")

vector_retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 10,
        "score_threshold": 0.3
    }
)

bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 10

retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5]
)