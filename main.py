#!/usr/bin/env python3
import argparse
import requests
import os

from bs4 import BeautifulSoup
from pprint import pprint


def google_SERP_links(num_results, **params):
    url = "https://customsearch.googleapis.com/customsearch/v1"

    links = []
    for start in range(1, num_results, 10):
        response = requests.get(
            url,
            params=params | {"start": start},
        )
        data = response.json()

        assert "items" in data  # Adjust this if this turns out to be problematic

        for webpage in data["items"]:
            links.append(webpage["link"])

    return links


def scrape_url_content(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Remove unwanted tags
            # for script in soup(["script", "style"]):
            #    script.extract()

            overall = ""
            bodies = soup.find_all("body")
            for body in bodies:
                # Extract visible text
                text = body.get_text()
                lines = (line.strip() for line in text.splitlines())
                overall += "\n".join(line for line in lines if line)
            return overall
        else:
            # Log these
            return ""
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""


if __name__ == "__main__":
    import tqdm

    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", type=str, help="Search query")
    parser.add_argument(
        "-t",
        "--total_pages",
        type=int,
        default=10,
        help="Number of articles to profile",
    )
    args = parser.parse_args()

    if not args.query:
        raise Exception("Please query something")

    if not os.getenv("CSE_SEARCH_ENGINE_ID"):
        os.environ["CSE_SEARCH_ENGINE_ID"] = (
            "b2d87ae5a9c2e40da"  # Default custom search engine for this project
        )

    params = {
        "q": args.query,
        "key": os.getenv("CSE_API_KEY"),
        "cx": os.getenv("CSE_SEARCH_ENGINE_ID"),
        "cr": "countryUS",
        # Filter by date of articles
    }

    webpages_info = {}
    for link in tqdm.tqdm(google_SERP_links(args.total_pages, **params)):
        raw_text = scrape_url_content(link)
        # text = clean_webpage(raw_text)
        webpages_info[link] = raw_text
        print(link)
        print(raw_text[500:])

    # Do something with webpages_info
