"""
Chat message component for displaying user and assistant messages
"""

import streamlit as st
from datetime import datetime


def display_user_message(content: str, timestamp: str = None):
    """
    Display a user message in the chat.

    Args:
        content: Message content
        timestamp: Message timestamp (optional)
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M")

    with st.chat_message("user"):
        st.markdown(content)
        st.caption(timestamp)


def display_assistant_message(
    content: str,
    citations: list = None,
    tokens: int = None,
    cost: float = None,
    timestamp: str = None
):
    """
    Display an assistant message in the chat.

    Args:
        content: Message content
        citations: List of citations
        tokens: Token count
        cost: Cost of generation
        timestamp: Message timestamp (optional)
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M")

    with st.chat_message("assistant"):
        st.markdown(content)

        # Display citations if provided
        if citations:
            with st.expander("📚 View Sources"):
                for i, citation in enumerate(citations[:5], 1):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(
                            f"**{citation['metadata'].get('paper_title', 'Unknown')}** "
                            f"({citation['metadata'].get('year', 'N/A')})"
                        )
                        st.caption(
                            f"By {citation['metadata'].get('authors', 'Unknown')} | "
                            f"Relevance: {citation['similarity_score']:.0%}"
                        )
                    with col2:
                        if st.button("Copy", key=f"cite_{i}"):
                            st.success("Citation copied!")

        # Display metrics if provided
        if tokens or cost:
            metric_text = []
            if tokens:
                metric_text.append(f"📊 {tokens} tokens")
            if cost:
                metric_text.append(f"💰 ${cost:.6f}")
            st.caption(" | ".join(metric_text))


def display_message_history(messages: list):
    """
    Display all messages in the chat history.

    Args:
        messages: List of message dictionaries
    """
    for message in messages:
        if message["role"] == "user":
            display_user_message(message["content"])
        else:
            display_assistant_message(
                content=message.get("content", ""),
                citations=message.get("citations"),
                tokens=message.get("tokens"),
                cost=message.get("cost")
            )


def copy_message_to_clipboard(content: str):
    """
    Copy message content to clipboard (client-side).

    Args:
        content: Content to copy
    """
    st.write(f"""
    <script>
        navigator.clipboard.writeText('{content}');
    </script>
    """, unsafe_allow_html=True)
