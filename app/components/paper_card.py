"""
Paper card component for displaying paper information
"""

import streamlit as st


def display_paper_card(paper: dict, show_abstract: bool = True):
    """
    Display a paper as a styled card.

    Args:
        paper: Paper metadata dictionary
        show_abstract: Whether to show abstract
    """
    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"### {paper.get('title', 'Unknown Title')}")
            st.markdown(
                f"**Authors:** {format_authors(paper.get('authors', []))}  \n"
                f"**Year:** {paper.get('year', 'N/A')} | "
                f"**ID:** {paper.get('id', 'Unknown')}"
            )

            if show_abstract and paper.get('abstract'):
                with st.expander("Abstract"):
                    st.markdown(paper['abstract'])

        with col2:
            if st.button("Search This Paper", key=f"search_{paper['id']}"):
                st.session_state.selected_paper = paper['id']
                st.success(f"Selected: {paper['id']}")


def format_authors(authors: list) -> str:
    """
    Format author list for display.

    Args:
        authors: List of author names

    Returns:
        Formatted author string
    """
    if not authors:
        return "Unknown"
    if len(authors) == 1:
        return authors[0]
    elif len(authors) == 2:
        return f"{authors[0]} and {authors[1]}"
    else:
        return f"{authors[0]} et al."


def display_paper_table(papers: list):
    """
    Display papers in a table format.

    Args:
        papers: List of paper metadata dictionaries
    """
    # Prepare data for table
    table_data = []
    for paper in papers:
        table_data.append({
            "ID": paper.get('id', 'N/A'),
            "Title": paper.get('title', 'Unknown')[:60] + "..." if len(paper.get('title', '')) > 60 else paper.get('title', 'Unknown'),
            "Authors": format_authors(paper.get('authors', [])),
            "Year": paper.get('year', 'N/A'),
        })

    st.dataframe(
        table_data,
        use_container_width=True,
        height=400
    )


def display_paper_details(paper: dict):
    """
    Display full paper details.

    Args:
        paper: Paper metadata dictionary
    """
    st.markdown(f"## {paper.get('title', 'Unknown Title')}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Authors", format_authors(paper.get('authors', [])))

    with col2:
        st.metric("Year", paper.get('year', 'N/A'))

    with col3:
        st.metric("Paper ID", paper.get('id', 'Unknown'))

    with col4:
        st.metric("Venue", paper.get('venue', 'N/A'))

    if paper.get('abstract'):
        st.markdown("### Abstract")
        st.markdown(paper['abstract'])

    if paper.get('doi'):
        st.markdown(f"**DOI:** [{paper['doi']}](https://doi.org/{paper['doi']})")

    if paper.get('topics'):
        st.markdown("### Topics")
        topic_str = ", ".join([f"🏷️ {topic}" for topic in paper['topics']])
        st.markdown(topic_str)
