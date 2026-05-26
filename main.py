from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from vector import retriever, vector_store


# MODEL

model = OllamaLLM(
        model="llama3.2:3b", 
        num_predict=1024,
        temperature=0.3
        )


# MEMORY

chat_history = InMemoryChatMessageHistory()
MAX_HISTORY = 8


# PROMPT

template = """
You are UPVerse, the official AI website assistant for the University of the Philippines Visayas (UPV) website.

STRICT RULES:
1. Answer ONLY using the retrieved context below. Do NOT use outside knowledge.
2. If the context does not contain the answer, say exactly:
   "I'm sorry, I could not find that information on the UPV website. Please contact the university for more information."
3. Do NOT guess, assume, or infer beyond what is written.
4. Give thorough, detailed and student-friendly answers. Do not cut answers short.
5. Use bullet points or numbered lists when listing items (e.g. officials, programs, requirements).
6. If relevant, mention offices, deadlines, programs, or links from the context.
7. If you are asked for the latest news or events, provide the most recent information from the retrieved context.

Conversation History:
{history}

Retrieved Context:
{context}

Question:
{question}

Answer (be detailed and complete — do not summarize unless asked):
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# FORMAT HISTORY
def format_chat_history(messages):
    history = []

    for msg in messages:
        if isinstance(msg, HumanMessage):
            history.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            history.append(f"Assistant: {msg.content}")

    return "\n".join(history)

# URL CLASSIFICATION

def classify_question(question: str) -> str | None:
    q = question.lower()
    if any(w in q for w in ["official", "chancellor", "president", "director", "dean", "administrator"]):
        return "officials"
    elif any(w in q for w in ["news", "announcement", "update", "event"]):
        return "news"
    elif any(w in q for w in ["program", "course", "degree", "college", "bachelor", "master"]):
        return "programs"
    elif any(w in q for w in ["admission", "apply", "enroll", "requirement", "application"]):
        return "admissions"
    elif any(w in q for w in ["job", "hiring", "career", "vacancy", "employment"]):
        return "careers"
    else:
        return None  # no filter, search everything




# MAIN FUNCTION (called by STREAMLIT)
def run_upverse(question: str):
    recent_messages = chat_history.messages[-MAX_HISTORY:]
    history_text = format_chat_history(recent_messages)

    
    last_user_msg = ""
    for msg in reversed(recent_messages):
        if isinstance(msg, HumanMessage):
            last_user_msg = msg.content
            break

    retrieval_query = f"{last_user_msg} {question}".strip()
    
    # Detect question type for filtering  
    question_type = classify_question(question)

    if question_type:
        # Filtered vector search
        filtered_docs = vector_store.similarity_search(
            retrieval_query,
            k=10,
            filter={"type": question_type}
        )
        # Fall back to unfiltered if nothing found
        if not filtered_docs:
            docs = retriever.invoke(retrieval_query)
        else:
            docs = filtered_docs
    else:
        docs = retriever.invoke(retrieval_query)

    context = "\n\n".join([
        f"SOURCE: {doc.metadata.get('url', 'Unknown')}\n\n{doc.page_content}"
        for doc in docs
    ])

    result = chain.invoke({
        "context": context,
        "question": question,
        "history": history_text
    })

    chat_history.add_message(HumanMessage(content=question))
    chat_history.add_message(AIMessage(content=result))

    return result, docs