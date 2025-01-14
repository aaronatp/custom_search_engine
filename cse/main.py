#!/usr/bin/env python3
import argparse
import os

import requests
from bs4 import BeautifulSoup


def google_SERP_links(num_results: int, **params: str | int) -> list[str]:
    """
    Fetch links from Google Search Engine Results Pages (SERPs) using a custom search engine API.

    Args:
        num_results (int): Number of results to fetch.
        **params: Additional parameters for the API request.

    Returns:
        List[str]: A list of URLs retrieved from the search results.
    """
    url = "https://customsearch.googleapis.com/customsearch/v1"

    links: list[str] = []
    for start in range(1, num_results, 10):
        response = requests.get(
            url,
            params=params | {"start": start},
        )
        # data actually has a predictable but complex dictionary structure
        # Is best practice simply to write Any or the full, complex structure?
        data = response.json()

        assert (
            "items" in data
        ), "The API response does not contain 'items'. Check the API response for issues."

        for webpage in data["items"]:
            links.append(webpage["link"])

    return links


def fetch_main_content(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unwanted elements
            for unwanted in soup(
                ["script", "style", "nav", "footer", "aside", "form"]
            ):
                unwanted.extract()

            # Target main content tags
            main_content = (
                soup.find("main") or soup.find("article") or soup.body
            )
            if main_content:
                text = main_content.get_text()
                lines = (line.strip() for line in text.splitlines())
                visible_text = "\n".join(
                    line for line in lines if line and len(line) > 50
                )
                return visible_text
        return "Failed to fetch content or no content available."
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

    params: dict[str, str] = {
        "q": args.query,
        "key": os.getenv("CSE_API_KEY"),
        "cx": os.getenv("CSE_SEARCH_ENGINE_ID"),
        "cr": "countryUS",
    }

    webpages_info: dict[str, str] = {}
    for link in tqdm.tqdm(google_SERP_links(args.total_pages, **params)):
        raw_text = fetch_main_content(link)
        webpages_info[link] = raw_text
        print(link)
        print(raw_text)  # Limit the output to the first 500 characters

    # Do something with webpages_info
