import requests
import re
import datetime

# Your OpenAlex Author ID (or query by ORCID / Name)
OPENALEX_AUTHOR_ID = "https://openalex.org/authors/a5082186830" # Siddharth Shukla
HTML_FILE_PATH = "index.html"

def fetch_citation_data():
    # Fetch author metrics from OpenAlex
    url = f"https://api.openalex.org/authors/{OPENALEX_AUTHOR_ID.split('/')[-1]}"
    response = requests.get(url).json()
    
    total_citations = response.get("cited_by_count", 0)
    h_index = response.get("summary_stats", {}).get("h_index", 0)
    i10_index = response.get("summary_stats", {}).get("i10_index", 0)
    
    # Fetch works
    works_url = response.get("works_api_url")
    works_data = requests.get(works_url).json().get("results", [])
    
    return {
        "citations": total_citations,
        "h_index": h_index,
        "i10_index": i10_index
    }, works_data

def update_html(metrics, works):
    with open(HTML_FILE_PATH, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Update summary numbers
    html_content = re.sub(r'<p id="total-citations">.*?</p>', f'<p id="total-citations">{metrics["citations"]}</p>', html_content)
    html_content = re.sub(r'<p id="h-index">.*?</p>', f'<p id="h-index">{metrics["h_index"]}</p>', html_content)
    html_content = re.sub(r'<p id="i10-index">.*?</p>', f'<p id="i10-index">{metrics["i10_index"]}</p>', html_content)

    # Update timestamp
    now = datetime.datetime.now().strftime("%B %d, %Y at %H:%M EST")
    html_content = re.sub(r'<span id="update-timestamp">.*?</span>', f'<span id="update-timestamp">{now}</span>', html_content)

    # Populate publications
    table_body = ""
    for work in works:
        title = work.get("title", "Untitled")
        year = work.get("publication_year", "N/A")
        cites = work.get("cited_by_count", 0)
        
        authorships = work.get("authorships", [])
        author_names = [a.get("author", {}).get("display_name", "") for a in authorships[:3]]
        authors_str = ", ".join(author_names) + ("..." if len(authorships) > 3 else "")

        table_body += f"""            <tr>
                <td><span class="paper-title">{title}</span><br>
                    <span class="paper-authors">{authors_str}</span></td>
                <td>{year}</td>
                <td style="text-align: right;"><span class="badge">{cites}</span></td>
            </tr>\n"""

    html_content = re.sub(r'(<tbody id="publications-body">)(.*?)(</tbody>)', f'\\1\n{table_body}\\3', html_content, flags=re.DOTALL)

    with open(HTML_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    metrics, works = fetch_citation_data()
    update_html(metrics, works)
