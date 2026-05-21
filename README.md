# UPVerse

**UPVerse** is a retrieval-augmented generation (RAG) system that transforms UP Visayas website content into an interactive AI assistant. It uses ChromaDB for vector search and Ollama LLMs for local inference, enabling fast and privacy-preserving question answering over UPV institutional data.



## 🚀 Features

- Semantic search over UPV website data
- Local LLM responses using Ollama (LLaMA 3.2)
- Retrieval-Augmented Generation (RAG) pipeline
- Knowledge base built from UPV official webpages
- Fast vector search using ChromaDB
- Interactive terminal-based chat assistant



## 🏗️ Project Structure

```bash
UPVerse/
├── main.py # Chat interface (LLM + retriever)
├── vector.py # Embedding + vector database setup
├── upv_data_cleaned.json # Scraped UPV website dataset
├── chroma_db/ # Local vector database (auto-generated)
├── requirements.txt # Python dependencies
└── README.md
```



## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/UPVerse.git
cd UPVerse
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the environment:

**Windows**

```bash
venv\Scripts\activate
```

**Mac/Linux**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
````

### 4. Install and setup Ollama

Download Ollama:
https://ollama.com

Pull required models:
```bash
ollama pull llama3.2
ollama pull mxbai-embed-large
```

### 5. Run the app
```bash
python main.py
```

## 💬 How to Use

After running the program, you can ask questions in the terminal:

```bash
Ask a question about UPV (q to quit): What is UP Visayas?
```

To exit, type: **q**

## 📦 Requirements

Main dependencies:

* langchain
* langchain-ollama
* langchain-chroma
* chromadb
* ollama

Install them using:
```bash
pip install -r requirements.txt
```

## Note

* UPVerse uses scraped UPV website data and may not always reflect the latest updates.
* This project runs locally and requires Ollama to be installed.
* Always verify important information from the official UPV website: https://www.upv.edu.ph


## 📄 License

This project is licensed under the MIT License.








