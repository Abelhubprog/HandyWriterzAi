from typing import List, Dict, Any
import requests
from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import Citation, CitationItem
from citeproc import formatter
from citeproc.source.json import CiteProcJSON

def get_csl_style(style_id: str = 'harvard-cite-them-right') -> CitationStylesStyle:
    """Fetches a CSL style file from the Zotero style repository."""
    url = f"https://www.zotero.org/styles/{style_id}"
    response = requests.get(url)
    response.raise_for_status()
    return CitationStylesStyle(response.text, validate=False)

def format_citations(csl_json: List[Dict[str, Any]], style_id: str) -> Dict[str, Any]:
    """
    Formats citations and a bibliography based on CSL JSON data and a style ID.
    """
    style = get_csl_style(style_id)
    bib_source = CiteProcJSON(csl_json)
    bibliography = CitationStylesBibliography(style, bib_source, formatter.html)

    citations = []
    for item in csl_json:
        citation_item = CitationItem(item['id'])
        citation = Citation([citation_item])
        bibliography.register(citation)
        citations.append({
            "id": item['id'],
            "in_text": bibliography.cite(citation)[0]
        })

    return {
        "in_text_citations": citations,
        "bibliography": [str(item) for item in bibliography.bibliography()]
    }

if __name__ == '__main__':
    # Example Usage
    sample_csl = [
        {
            "id": "example_1",
            "type": "article-journal",
            "title": "The Impact of AI on Academic Research",
            "author": [{"family": "Smith", "given": "John"}],
            "issued": {"date-parts": [[2023]]}
        }
    ]
    
    formatted = format_citations(sample_csl, 'apa')
    print("In-text citations:")
    for cit in formatted['in_text_citations']:
        print(f"  {cit['id']}: {cit['in_text']}")
        
    print("\nBibliography:")
    for entry in formatted['bibliography']:
        print(f"  {entry}")