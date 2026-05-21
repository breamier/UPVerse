import json
import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter 

# Load JSON data
with open("upv_data_cleaned.json", "r", encoding="utf-8") as f:
    data = json.load(f)

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = "./upv_chroma_db"
add_documents = not os.path.exists(db_location)

if add_documents:
    raw_documents = []
    for index, item in enumerate(data):
        page_content = f"Title: {item.get('title', '')}\nContent: {item.get('content', '')}"
        
        metadata = {
            "url": item.get("url", ""), 
            "type": item.get("type", "")
        }
        raw_documents.append(Document(page_content=page_content, metadata=metadata))

    # Split large documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,       
        chunk_overlap=150, 
        separators=["\n\n", "\n", " ", ""]
    )
    documents = text_splitter.split_documents(raw_documents)
    
    # CreateIDs for every chunk
    ids = [str(i) for i in range(len(documents))]

# Initialize ChromaDB
vector_store = Chroma(collection_name="upv_website_data", embedding_function=embeddings, persist_directory=db_location)

if add_documents:
    print(f"Embedding {len(documents)} text chunks into ChromaDB. This might take a moment...")
    vector_store.add_documents(documents=documents, ids=ids)
    print("Embedding complete!")

retriever = vector_store.as_retriever(
    search_kwargs={"k": 5} # Looks up the top 5 most relevant information
)