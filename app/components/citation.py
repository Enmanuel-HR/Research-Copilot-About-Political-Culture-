"""
Citation formatter and display component
"""

import streamlit as st


class CitationFormatter:
    """Handle citation formatting in multiple styles"""

    @staticmethod
    def format_apa(paper_title: str, authors: str, year: int) -> str:
        """
        Format citation in APA style.

        Args:
            paper_title: Paper title
            authors: Author names
            year: Publication year

        Returns:
            APA formatted citation
        """
        return f"{authors} ({year}). {paper_title}."

    @staticmethod
    def format_mla(paper_title: str, authors: str, year: int) -> str:
        """
        Format citation in MLA style.

        Args:
            paper_title: Paper title
            authors: Author names
            year: Publication year

        Returns:
            MLA formatted citation
        """
        return f"{authors}. \"{paper_title}.\" {year}."

    @staticmethod
    def format_chicago(paper_title: str, authors: str, year: int) -> str:
        """
        Format citation in Chicago style.

        Args:
            paper_title: Paper title
            authors: Author names
            year: Publication year

        Returns:
            Chicago formatted citation
        """
        return f"{authors}. \"{paper_title}.\" {year}."

    @staticmethod
    def format_bibtex(paper_id: str, authors: str, year: int, title: str) -> str:
        """
        Format citation as BibTeX entry.

        Args:
            paper_id: Paper identifier
            authors: Author names
            year: Publication year
            title: Paper title

        Returns:
            BibTeX formatted citation
        """
        return f"""@article{{{paper_id},
    author = {{{authors}}},
    title = {{{title}}},
    year = {{{year}}}
}}"""


def display_citation_box(citation_dict: dict, style: str = "APA"):
    """
    Display a citation in a formatted box.

    Args:
        citation_dict: Citation information dictionary
        style: Citation style (APA, MLA, Chicago, BibTeX)
    """
    formatter = CitationFormatter()

    paper_title = citation_dict.get('metadata', {}).get('paper_title', 'Unknown')
    authors = citation_dict.get('metadata', {}).get('authors', 'Unknown')
    year = citation_dict.get('metadata', {}).get('year', 'N/A')
    paper_id = citation_dict.get('chunk_id', 'unknown').split('_')[0]

    # Format citation based on style
    if style == "APA":
        formatted = formatter.format_apa(paper_title, authors, year)
    elif style == "MLA":
        formatted = formatter.format_mla(paper_title, authors, year)
    elif style == "Chicago":
        formatted = formatter.format_chicago(paper_title, authors, year)
    elif style == "BibTeX":
        formatted = formatter.format_bibtex(paper_id, authors, year, paper_title)
    else:
        formatted = formatter.format_apa(paper_title, authors, year)

    st.markdown(f"""
    <div class='citation-box'>
        {formatted}
    </div>
    """, unsafe_allow_html=True)

    # Copy button
    if st.button("Copy Citation", key=f"copy_{paper_id}"):
        st.success("Citation copied to clipboard!")


def display_citation_list(citations: list, style: str = "APA"):
    """
    Display multiple citations.

    Args:
        citations: List of citation dictionaries
        style: Citation style
    """
    st.markdown("## References")

    for i, citation in enumerate(citations, 1):
        with st.expander(f"Source {i}: {citation.get('metadata', {}).get('paper_title', 'Unknown')[:50]}"):
            display_citation_box(citation, style)


def display_bibliography_export(citations: list, style: str = "APA") -> str:
    """
    Generate bibliography for export.

    Args:
        citations: List of citation dictionaries
        style: Citation style

    Returns:
        Formatted bibliography string
    """
    formatter = CitationFormatter()
    bibliography_lines = []

    for citation in citations:
        paper_title = citation.get('metadata', {}).get('paper_title', 'Unknown')
        authors = citation.get('metadata', {}).get('authors', 'Unknown')
        year = citation.get('metadata', {}).get('year', 'N/A')

        if style == "APA":
            line = formatter.format_apa(paper_title, authors, year)
        elif style == "MLA":
            line = formatter.format_mla(paper_title, authors, year)
        elif style == "Chicago":
            line = formatter.format_chicago(paper_title, authors, year)
        else:
            line = formatter.format_apa(paper_title, authors, year)

        bibliography_lines.append(line)

    return "\n\n".join(bibliography_lines)


def citation_manager_ui():
    """
    Display citation manager interface.
    """
    st.markdown("## Citation Manager")

    # Style selection
    style = st.selectbox(
        "Citation Style:",
        ["APA", "MLA", "Chicago", "BibTeX"]
    )

    # Sample citations (in real app, these would come from session state)
    sample_citations = [
        {
            "metadata": {
                "paper_title": "Youth protest culture in Lima (2011-2016)",
                "authors": "Patricia Oliart",
                "year": 2022
            },
            "chunk_id": "paper_017_chunk_0"
        },
        {
            "metadata": {
                "paper_title": "Political Goals of Peruvian Students",
                "authors": "David Post",
                "year": 1988
            },
            "chunk_id": "paper_018_chunk_0"
        }
    ]

    # Display citations
    for citation in sample_citations:
        with st.expander(f"{citation['metadata']['authors']} ({citation['metadata']['year']})"):
            display_citation_box(citation, style)

    # Export options
    st.markdown("### Export Bibliography")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Export as .txt"):
            bibliography = display_bibliography_export(sample_citations, style)
            st.download_button(
                label="Download .txt",
                data=bibliography,
                file_name=f"bibliography_{style.lower()}.txt",
                mime="text/plain"
            )

    with col2:
        if st.button("Copy All"):
            st.success("Bibliography copied!")

    with col3:
        if st.button("Generate BibTeX"):
            bibtex = display_bibliography_export(sample_citations, "BibTeX")
            st.download_button(
                label="Download .bib",
                data=bibtex,
                file_name="bibliography.bib",
                mime="text/plain"
            )
