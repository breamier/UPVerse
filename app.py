import streamlit as st

from langchain_core.messages import HumanMessage, AIMessage

from main import (
    retriever,
    model,
    chain,
    chat_history,
    format_chat_history,
    MAX_HISTORY
)

# PAGE CONFIG
st.set_page_config(
    page_title="UPVerse",
    page_icon="assets/upvlogo.png",
    layout="centered"
)

st.logo("assets/upvlogo.png")
st.title("UPVerse")
st.caption("University of the Philippines Visayas AI Assistant")

# INIT SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hi! I'm UPVerse, your AI assistant for the University of the Philippines Visayas. How can I help you today?"
    })

# DISPLAY CHAT HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# INPUT BOX
question = st.chat_input("Ask something about UP Visayas...")

# ON USER INPUT
if question:

    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    # FORMAT HISTORY
    recent_messages = chat_history.messages[-MAX_HISTORY:]
    history_text = format_chat_history(recent_messages)

    # RETRIEVAL
    retrieval_query = f"""
        Conversation:
        {history_text}

        Current Question:
        {question}
        """

    docs = retriever.invoke(retrieval_query)

    context = "\n\n".join([
        f"SOURCE: {doc.metadata.get('url', 'Unknown')}\n\n{doc.page_content}"
        for doc in docs
    ])

    # CALL LLM
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            result = chain.invoke({
                "context": context,
                "question": question,
                "history": history_text
            })

            st.write(result)

            
            # SOURCES
            with st.expander("Sources"):
                for i, doc in enumerate(docs):
                    st.write(f"{i+1}. {doc.metadata.get('url', 'Unknown')}")

    # SAVE MEMORY
    chat_history.add_message(
        HumanMessage(content=question)
    )

    chat_history.add_message(
        AIMessage(content=result)
    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": result
    })