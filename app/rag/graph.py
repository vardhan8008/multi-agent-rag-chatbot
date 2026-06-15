from typing import Annotated, List, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from app.rag import vectorstore
from app.rag.llm import get_llm


class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    question: str
    route: str
    context: str
    sources: List[dict]


def format_history(messages: List[BaseMessage], limit: int = 6) -> str:
    lines = []
    for message in messages[-limit:]:
        role = "User" if isinstance(message, HumanMessage) else "Assistant"
        lines.append(f"{role}: {message.content}")
    return "\n".join(lines)


def analyze(state: ChatState) -> dict:
    question = state["question"]

    if vectorstore.count() == 0:
        return {"route": "chat", "question": question}

    history = format_history(state["messages"][:-1])
    prompt = (
        "Decide how to handle a message in a document Q&A assistant.\n"
        "Reply with 'retrieve' if the answer needs the uploaded documents, "
        "or 'chat' for greetings and small talk.\n"
        "Then write a standalone search query that resolves pronouns using the "
        "conversation. For 'chat', repeat the message.\n\n"
        f"Conversation:\n{history or '(none)'}\n\n"
        f"Message: {question}\n\n"
        "ROUTE: <retrieve|chat>\nQUERY: <text>"
    )

    response = get_llm().invoke(prompt).content
    route, query = "retrieve", question
    for line in response.splitlines():
        lower = line.lower()
        if lower.startswith("route:"):
            route = "chat" if "chat" in lower else "retrieve"
        elif lower.startswith("query:"):
            query = line.split(":", 1)[1].strip() or question

    return {"route": route, "question": query}


def retrieve(state: ChatState) -> dict:
    docs = vectorstore.search(state["question"])
    context = "\n\n".join(
        f"[{i + 1}] (from {doc.metadata.get('source')})\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )
    sources = [
        {"source": doc.metadata.get("source"), "snippet": doc.page_content[:200]}
        for doc in docs
    ]
    return {"context": context, "sources": sources}


def generate(state: ChatState) -> dict:
    system = SystemMessage(
        content=(
            "Answer the question using the context below and the conversation "
            "history. If the answer is not in the context, say so. Cite sources "
            "inline like [1], [2].\n\n"
            f"Context:\n{state['context']}"
        )
    )
    history = [m for m in state["messages"] if isinstance(m, (HumanMessage, AIMessage))][:-1]
    messages = [system, *history, HumanMessage(content=state["question"])]
    answer = get_llm().invoke(messages).content
    return {"messages": [AIMessage(content=answer)]}


def chat(state: ChatState) -> dict:
    system = SystemMessage(
        content=(
            "You are a helpful assistant for a document Q&A app. Keep replies "
            "short and invite the user to upload a document or ask about one."
        )
    )
    history = [m for m in state["messages"] if isinstance(m, (HumanMessage, AIMessage))]
    answer = get_llm().invoke([system, *history]).content
    return {"messages": [AIMessage(content=answer)]}


def build_graph():
    builder = StateGraph(ChatState)
    builder.add_node("analyze", analyze)
    builder.add_node("retrieve", retrieve)
    builder.add_node("generate", generate)
    builder.add_node("chat", chat)

    builder.add_edge(START, "analyze")
    builder.add_conditional_edges(
        "analyze",
        lambda state: state["route"],
        {"retrieve": "retrieve", "chat": "chat"},
    )
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", END)
    builder.add_edge("chat", END)

    return builder.compile(checkpointer=MemorySaver())


graph = build_graph()


def run_turn(session_id: str, message: str) -> dict:
    config = {"configurable": {"thread_id": session_id}}
    result = graph.invoke(
        {"messages": [HumanMessage(content=message)], "question": message},
        config=config,
    )
    return {
        "answer": result["messages"][-1].content,
        "route": result.get("route", "chat"),
        "sources": result.get("sources", []),
    }


def get_history(session_id: str) -> List[dict]:
    config = {"configurable": {"thread_id": session_id}}
    snapshot = graph.get_state(config)
    messages = snapshot.values.get("messages", []) if snapshot else []
    turns = []
    for message in messages:
        if isinstance(message, HumanMessage):
            turns.append({"role": "user", "content": message.content})
        elif isinstance(message, AIMessage):
            turns.append({"role": "assistant", "content": message.content})
    return turns

 