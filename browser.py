from playwright.sync_api import sync_playwright

"""
- on BTS transtats website, some sites are blocked via Akamai CDN making bot and webscraping difficult with requests and bs4 alone.
- using playwright to support browser automation.  
"""

# create method to simulate playwright browser access
def fetch_html(url: str):

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(url, wait_until="networkidle")

        html = page.content()

        browser.close()

    return html