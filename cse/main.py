#!/usr/bin/env python3
import argparse
import requests
from bs4 import BeautifulSoup
import os
from typing import List, Dict, Union


def google_SERP_links(
    num_results: int, **params: Union[str, int]
) -> List[str]:
    """
    Fetch links from Google Search Engine Results Pages (SERPs) using a custom search engine API.

    Args:
        num_results (int): Number of results to fetch.
        **params: Additional parameters for the API request.

    Returns:
        List[str]: A list of URLs retrieved from the search results.
    """
    url = "https://customsearch.googleapis.com/customsearch/v1"
    links: List[str] = []

    for start in range(1, num_results, 10):
        response = requests.get(
            url,
            params=params | {"start": start},
        )
        data = response.json()

        assert (
            "items" in data
        ), "The API response does not contain 'items'. Check the API response for issues."

        for webpage in data["items"]:
            links.append(webpage["link"])

    return links


def scrape_url_content(url: str) -> str:
    """
    Scrape the content of a given URL.

    Args:
        url (str): The URL to scrape.

    Returns:
        str: The textual content extracted from the webpage.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            overall: str = ""
            bodies = soup.find_all("body")

            for body in bodies:
                text = body.get_text()
                lines = (line.strip() for line in text.splitlines())
                overall += "\n".join(line for line in lines if line)

            return overall
        else:
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
        raise ValueError(
            "Please specify a query using the -q or --query argument."
        )

    if not os.getenv("CSE_SEARCH_ENGINE_ID"):
        os.environ["CSE_SEARCH_ENGINE_ID"] = (
            "b2d87ae5a9c2e40da"  # Default custom search engine for this project
        )

    params: Dict[str, Union[str, int]] = {
        "q": args.query,
        "key": os.getenv("CSE_API_KEY", ""),
        "cx": os.getenv("CSE_SEARCH_ENGINE_ID", ""),
        "cr": "countryUS",
    }

    webpages_info: Dict[str, str] = {}
    for link in tqdm.tqdm(google_SERP_links(args.total_pages, **params)):
        raw_text = scrape_url_content(link)
        webpages_info[link] = raw_text
        print(link)
        print(raw_text[:500])  # Limit the output to the first 500 characters

    # Do something with webpages_info
