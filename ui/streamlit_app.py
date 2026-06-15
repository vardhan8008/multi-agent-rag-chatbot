import os
import uuid

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Conversational RAG", layout="centered")

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []


def show_sources(sources):
    if not sources:
        return
    with st.expander("Sources"):
        for i, source in enumerate(sources, 1):
            st.markdown(f"**[{i}] {source['source']}**")
            st.caption(source["snippet"])


with st.sidebar:
    st.header("Documents")
    uploaded = st.file_uploader("Upload a document", type=["pdf", "txt", "md"])
    if uploaded and st.button("Index document"):
        with st.spinner("Indexing..."):
            response = requests.post(
                f"{API_URL}/upload",
                files={"file": (uploaded.name, uploaded.getvalue())},
            )
        if response.ok:
            st.success(response.json()["message"])
        else:
            st.error(response.json().get("detail", "Upload failed"))

    st.divider()
    st.caption(f"Session: {st.session_state.session_id}")
    if st.button("New conversation"):
        st.session_state.session_id = uuid.uuid4().hex[:8]
        st.session_state.messages = []
        st.rerun()


st.title("Conversational RAG")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        show_sources(message.get("sources"))

if prompt := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{API_URL}/chat",
                json={"session_id": st.session_state.session_id, "message": prompt},
            )
        data = response.json()
        answer = data["answer"]
        sources = data.get("sources", [])
        st.markdown(answer)
        show_sources(sources)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )
 