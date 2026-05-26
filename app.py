import streamlit as st

from langchain_core.messages import HumanMessage, AIMessage

from main import (
    retriever,
    model,
    chain,
    chat_history,
    format_chat_history,
    MAX_HISTORY,
    run_upverse
)

# PAGE CONFIG
st.set_page_config(
    page_title="UPVerse",
    page_icon="assets/upvlogo.png",
    layout="centered"
)

# CSS
st.markdown("""
<style>
.main-title {
    font-size: 3.8rem;
    font-weight: 700;
    color: #8D1436;
    text-align: center;
    letter-spacing: -1px;
}
.main-subtitle {
    text-align: center;
    opacity: 0.75;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# HEADER
st.logo("assets/upvlogo.png")
st.markdown('<div class="main-title">UPVerse</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">University of the Philippines Visayas AI Assistant</div>', unsafe_allow_html=True)

# INIT SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hi! I'm UPVerse, your AI assistant for the University of the Philippines Visayas. How can I help you today?"
    })

# AVATARS
AVATARS = {"user": "assets/user.png", "assistant": "assets/chatbot.png"}

# DISPLAY CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=AVATARS[msg["role"]]):
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

    with st.chat_message("user", avatar=AVATARS["user"]):
        st.write(question)


    # CALL LLM
    with st.chat_message("assistant",  avatar=AVATARS["assistant"]):
        with st.spinner("Thinking..."):
            result, docs = run_upverse(question)
            st.write(result)

            
            # SOURCES
            with st.expander("Sources"):
                for i, doc in enumerate(docs):
                    st.write(f"{i+1}. {doc.metadata.get('url', 'Unknown')}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result
    })