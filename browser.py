from playwright.sync_api import sync_playwright

"""
- on BTS transtats website, some sites are blocked via Akamai CDN making bot and webscraping difficult with requests and bs4 alone.
- using playwright to support browser automation.

TODO:  
"""

# create method to simulate playwright browser access
def fetch_html(url: str):



    # browser is run on chromium
    with sync_playwright() as p:

        print("starting playwright browser..")

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(url, wait_until="networkidle")

        print("page(HTML) content received!")
        html = page.content() # returned html content

        print("closing playwright browser.")
        browser.close()

    return html