"""
Research Copilot - Main Streamlit Application
Academic assistant for interactive paper analysis and Q&A
"""

import streamlit as st
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from src.embedding import OpenAIEmbedder
from src.vectorstore import ChromaVectorStore
from src.retrieval import RAGRetriever
from src.generation import RAGGenerator

# Page configuration
st.set_page_config(
    page_title="Research Copilot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for academic theme
st.markdown("""
<style>
    :root {
        --primary-color: #1F4788;
        --secondary-color: #D4A574;
        --accent-color: #2E7D32;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --error-color: #F44336;
    }

    .main-header {
        font-family: 'Georgia', serif;
        color: #1a1a2e;
        border-bottom: 3px solid var(--primary-color);
        padding-bottom: 10px;
    }

    .citation-box {
        background-color: #f0f0f5;
        border-left: 4px solid var(--primary-color);
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
    }

    .paper-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .paper-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        border-color: var(--primary-color);
    }

    .user-message {
        background-color: #e3f2fd;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
    }

    .assistant-message {
        background-color: #f5f5f5;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
    }

    .strategy-badge {
        display: inline-block;
        background-color: var(--secondary-color);
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        margin: 5px 5px 5px 0;
    }

    .metric-card {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
    }

    .metric-value {
        font-size: 2em;
        font-weight: bold;
        margin: 10px 0;
    }

    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "embedder" not in st.session_state:
        st.session_state.embedder = OpenAIEmbedder()

    if "vector_store" not in st.session_state:
        st.session_state.vector_store = ChromaVectorStore(
            persist_directory=str(config.CHROMA_DB_DIR)
        )
        st.session_state.vector_store.create_collection(
            config.CHROMA_COLLECTION_NAME
        )

    if "retriever" not in st.session_state:
        st.session_state.retriever = RAGRetriever(
            vector_store=st.session_state.vector_store,
            embedder=st.session_state.embedder,
            paper_catalog_path=str(config.PAPERS_DIR / "paper_catalog.json")
        )

    if "generator" not in st.session_state:
        st.session_state.generator = RAGGenerator(
            strategy="clear_instructions",
            temperature=0.5
        )

    if "paper_catalog" not in st.session_state:
        try:
            catalog_path = config.PAPERS_DIR / "paper_catalog.json"
            with open(catalog_path, 'r', encoding='utf-8') as f:
                catalog_data = json.load(f)
                st.session_state.paper_catalog = catalog_data.get('papers', [])
        except FileNotFoundError:
            st.session_state.paper_catalog = []

    if "query_count" not in st.session_state:
        st.session_state.query_count = 0

    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0

    if "total_cost" not in st.session_state:
        st.session_state.total_cost = 0.0

init_session_state()

# Load paper catalog helper
def get_paper_titles():
    """Get list of all paper titles"""
    return [f"{p['id']}: {p['title']}" for p in st.session_state.paper_catalog]

def get_paper_by_id(paper_id):
    """Get paper data by ID"""
    for paper in st.session_state.paper_catalog:
        if paper['id'] == paper_id:
            return paper
    return None

# Display helper functions
def display_citation(citation):
    """Display a single citation in APA format"""
    apa_format = f"{citation['metadata'].get('authors', 'Unknown')} ({citation['metadata'].get('year', 'N/A')}). {citation['metadata'].get('paper_title', 'Unknown paper')}."
    st.markdown(f"<div class='citation-box'>{apa_format}</div>", unsafe_allow_html=True)

def display_citations(citations):
    """Display all citations from retrieved chunks"""
    if citations:
        st.markdown("**Sources:**")
        for i, citation in enumerate(citations[:5], 1):  # Show top 5 citations
            with st.expander(f"Source {i}: {citation['metadata'].get('paper_title', 'Unknown')[:50]}..."):
                st.markdown(f"**Authors:** {citation['metadata'].get('authors', 'Unknown')}")
                st.markdown(f"**Year:** {citation['metadata'].get('year', 'N/A')}")
                st.markdown(f"**Relevance Score:** {citation['similarity_score']:.1%}")
                st.markdown(f"**Text:** {citation['text'][:300]}...")

# Sidebar
with st.sidebar:
    st.markdown("# 📚 Research Copilot")
    st.markdown("*Your AI research assistant for academic papers*")

    st.markdown("---")

    # Paper filter section
    st.markdown("### Paper Filters")

    # Select papers to search
    selected_paper_options = get_paper_titles()
    selected_papers_str = st.multiselect(
        "Search in papers:",
        options=selected_paper_options,
        help="Leave empty to search all papers"
    )

    # Extract paper IDs from selection
    selected_paper_ids = [s.split(":")[0] for s in selected_papers_str] if selected_paper_options else []

    # Strategy selector
    st.markdown("### Generation Strategy")
    strategy_map = {
        "V1: Clear Instructions": "clear_instructions",
        "V2: Structured JSON": "structured_output",
        "V3: Few-Shot Learning": "few_shot_learning",
        "V4: Chain-of-Thought": "chain_of_thought"
    }

    selected_strategy_name = st.selectbox(
        "Prompt Strategy:",
        list(strategy_map.keys()),
        help="Choose the response format that best fits your needs"
    )
    selected_strategy = strategy_map[selected_strategy_name]

    # Update generator strategy
    st.session_state.generator.change_strategy(selected_strategy)

    st.markdown("---")

    # Session statistics
    st.markdown("### Session Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Queries</div><div class='metric-value'>{st.session_state.query_count}</div></div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Tokens</div><div class='metric-value'>{st.session_state.total_tokens}</div></div>", unsafe_allow_html=True)

    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Cost</div><div class='metric-value'>${st.session_state.total_cost:.3f}</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Actions
    st.markdown("### Actions")
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.session_state.total_tokens = 0
        st.session_state.total_cost = 0.0
        st.rerun()

    st.markdown("---")
    st.markdown("*Built with OpenAI GPT-4 and ChromaDB*")

# Main chat area
st.markdown("<h1 class='main-header'>💬 Chat with Your Research Papers</h1>", unsafe_allow_html=True)

st.markdown("""
Ask questions about the academic papers in your collection. The Research Copilot will search
the papers, retrieve relevant passages, and generate comprehensive answers with proper citations.
""")

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
            if "strategy" in message:
                st.markdown(f"<span class='strategy-badge'>{message['strategy']}</span>", unsafe_allow_html=True)
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])
            if "citations" in message:
                display_citations(message["citations"])
            if "tokens" in message:
                st.caption(f"📊 {message['tokens']} tokens used | Cost: ${message['cost']:.6f}")

# Chat input
st.markdown("---")

col1, col2 = st.columns([0.9, 0.1])

with col1:
    prompt = st.chat_input(
        "Ask a question about your papers...",
        key="chat_input"
    )

with col2:
    pass  # Placeholder for alignment

if prompt:
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "strategy": selected_strategy_name
    })

    # Get response
    with st.spinner("🔍 Searching papers... Generating answer..."):
        try:
            # Retrieve relevant chunks
            retrieved_chunks = st.session_state.retriever.retrieve(
                query=prompt,
                k=5,
                similarity_threshold=None,
                filter_paper_id=selected_paper_ids[0] if len(selected_paper_ids) == 1 else None
            )

            # Format context
            context = st.session_state.retriever.get_retrieval_context(
                retrieved_chunks,
                include_metadata=True
            )

            # Generate answer
            result = st.session_state.generator.generate(
                question=prompt,
                context=context,
                max_tokens=800
            )

            # Add assistant message to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "citations": retrieved_chunks,
                "tokens": result["tokens"]["total"],
                "cost": result["cost"]
            })

            # Update session statistics
            st.session_state.query_count += 1
            st.session_state.total_tokens += result["tokens"]["total"]
            st.session_state.total_cost += result["cost"]

            # Rerun to display new messages
            st.rerun()

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            st.info("Please check that your OpenAI API key is properly configured.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.9em;'>
    <p>Research Copilot v1.0 | Powered by OpenAI GPT-4 & ChromaDB</p>
    <p>For questions or issues, please refer to the documentation.</p>
</div>
""", unsafe_allow_html=True)
