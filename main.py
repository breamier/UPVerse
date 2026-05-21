from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

model = OllamaLLM(model="llama3.2")

template = """
You are a helpful, knowledgeable, and polite university website assistant for the University of the Philippines Visayas (UPV). 

Use the following information scraped directly from the UPV website to answer the user's question accurately. If the answer is not contained within the provided information, politely state that you do not know, but offer to help with something else. Do not invent information.

Relevant UPV Information:
{context}

User Question: {question}

Answer:
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

while True:
    print("\n\n------------------------------")
    question = input("Ask a question about UPV (q to quit): ")
    print("\n\n")
    if question.lower() == "q":
        break

    # Retrieve relevant documents from ChromaDB
    retrieved_docs = retriever.invoke(question)
    
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    # Feed the context and question to the LLM
    result = chain.invoke({"context": context, "question": question})
    print(result)