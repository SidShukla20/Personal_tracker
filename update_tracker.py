import datetime
from scholarly import scholarly
import re

# Your unique Google Scholar ID from the URL
SCHOLAR_ID = "DGfMrEsAAAAJ"
HTML_FILE_PATH = "index.html"

def update_html(citation_data, publication_data):
    """Updates the HTML dashboard with new data."""
    try:
        with open(HTML_FILE_PATH, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Update Summary Stats
        html_content = re.sub(r'<p id="total-citations">.*?</p>', 
                              f'<p id="total-citations">{citation_data.get("citedby", 0)}</p>', html_content)
        html_content = re.sub(r'<p id="h-index">.*?</p>', 
                              f'<p id="h-index">{citation_data.get("hindex", 0)}</p>', html_content)
        html_content = re.sub(r'<p id="i10-index">.*?</p>', 
                              f'<p id="i10-index">{citation_data.get("i10index", 0)}</p>', html_content)

        # Update Timestamp
        now = datetime.datetime.now().strftime("%B %d, %Y at %H:%M EST")
        html_content = re.sub(r'<span id="update-timestamp">.*?</span>', 
                              f'<span id="update-timestamp">{now}</span>', html_content)

        # Build Publication Table Body
        table_body = ""
        for pub in publication_data:
            title = pub['bib'].get('title', 'Unknown Title')
            author_list = pub['bib'].get('author', 'Unknown Authors')
            # Limit authors for cleaner display
            authors = ', '.join(author_list[:3]) + ('...' if len(author_list) > 3 else '')
            year = pub['bib'].get('pub_year', 'Unknown Year')
            citations = pub.get('num_citations', 0)
            
            table_row = f"""            <tr>
                <td><span class="paper-title">{title}</span><br>
                    <span style="font-size:0.9em;color:#666">{authors}</span></td>
                <td>{year}</td>
                <td><span class="badge">{citations}</span></td>
            </tr>
"""
            table_body += table_row

        # Replace the table body content
        # Matches content between <tbody id="publications-body"> and </tbody>
        html_content = re.sub(r'(<tbody id="publications-body">)(.*?)(</tbody>)', 
                              f'\\1\n{table_body}\\3', html_content, flags=re.DOTALL)

        # Save the updated file
        with open(HTML_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Successfully updated {HTML_FILE_PATH} at {now}")

    except FileNotFoundError:
        print(f"❌ Error: {HTML_FILE_PATH} not found. Please create the file from the provided design.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

def get_scholar_data(scholar_id):
    """Fetches citation and publication data from Google Scholar."""
    print(f"Fetching data for Scholar ID: {scholar_id}...")
    
    # 1. Fetch author profile
    author = scholarly.search_author_id(scholar_id)
    author = scholarly.fill(author, sections=['counts', 'publications'])
    
    # Extract needed citation metrics
    citation_data = {
        'citedby': author['citedby'],
        'hindex': author['hindex'],
        'i10index': author['i10index']
    }
    
    # 2. Fetch and sort publication data
    all_pubs = []
    print("Loading full publication details (this might take a minute)...")
    for pub in author['publications']:
        # Fetching full details ensures we get authors/year accurately
        # fill(pub) can be slow for large bibliographies, handle with care.
        # fill_pub = scholarly.fill(pub) 
        all_pubs.append(pub)
        # Process first 10 for demonstration; remove [:10] for all.
        # if len(all_pubs) >= 10: break 

    print(f"Processed {len(all_pubs)} publications.")
    
    return citation_data, all_pubs

if __name__ == "__main__":
    # 1. Fetch New Data
    citation_data, publication_data = get_scholar_data(SCHOLAR_ID)
    
    # 2. Update the HTML file
    update_html(citation_data, publication_data)
