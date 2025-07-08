from src.models import SourceRecord

def _format_authors(authors: list) -> str:
    """Formats a list of authors into a standard string."""
    if not authors:
        return ""
    # Simple author formatting, can be expanded for APA/MLA etc.
    return ", ".join(authors)

def _format_book(source: SourceRecord) -> str:
    """Formats a citation for a 'book' source."""
    authors = _format_authors(source.authors)
    year = source.publication_year or "n.d."
    title = source.title or "[No Title]"
    publisher = source.publisher or ""
    
    parts = [f"{authors} ({year}).", title]
    if publisher:
        parts.append(publisher)
        
    return " ".join(part.strip('.') for part in parts) + "."

def _format_article(source: SourceRecord) -> str:
    """Formats a citation for an 'article' source."""
    authors = _format_authors(source.authors)
    year = source.publication_year or "n.d."
    title = source.title or "[No Title]"
    journal = source.publisher or "[No Journal]" # 'publisher' field used for journal
    
    return f"{authors} ({year}). {title}. {journal}."

def _format_website(source: SourceRecord) -> str:
    """Formats a citation for a 'website' source."""
    authors = _format_authors(source.authors) or "n.a."
    title = source.title or "[No Title]"
    url = source.url or "[No URL]"
    
    return f"{authors}. {title}. Retrieved from {url}"

def _format_report(source: SourceRecord) -> str:
    """Formats a citation for a 'report' source."""
    authors = _format_authors(source.authors)
    year = source.publication_year or "n.d."
    title = source.title or "[No Title]"
    report_num_part = f" (Report No. {source.report_number})" if source.report_number else ""
    
    return f"{authors} ({year}). {title}{report_num_part}."

def _format_default(source: SourceRecord) -> str:
    """A fallback for any source type without a specific format."""
    authors = _format_authors(source.authors)
    year = source.publication_year
    title = source.title
    
    return f"{authors} - {title} ({year})"

# A mapping from source type value to the appropriate formatting function
CITATION_FORMATTERS = {
    "book": _format_book,
    "article": _format_article,
    "website": _format_website,
    "report": _format_report,
    "standard": _format_report, # Using report format for standard
    "manual": _format_book, # Using book format for manual
}

def generate_citation(source: SourceRecord) -> str:
    """
    Generates a citation string for a source based on its type.

    Args:
        source: The SourceRecord object.

    Returns:
        A formatted citation string.
    """
    formatter = CITATION_FORMATTERS.get(source.source_type.value, _format_default)
    return formatter(source)