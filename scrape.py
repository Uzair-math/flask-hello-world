from firecrawl import FirecrawlApp
import asyncio
from typing import List, Dict

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

# app = FirecrawlApp(api_key="api")
app = FirecrawlApp(api_key="fc-da775755d8104b52be218f46ac69fa9f")

REPLIT_BOUNTIES_URL = 'https://replit.com/bounties?status=open&order=creationDateDescending'

extract_prompt = (
    "Extract all open bounties from this page. "
    "For each bounty, return a list of objects with these fields: "
    "title, link, value, and posted_time. "
    "The link should be the full URL to the bounty. "
    "The value should be the bounty reward (e.g. $100 or 10,000 Cycles). "
    "The posted_time should be the time since the bounty was posted (e.g. '2 hours ago'). "
    "Return the result as a JSON object with a 'bounties' key containing the list."
)

def print_bounties(bounties: List[Dict]):
    if not bounties:
        print("No bounties found or extraction failed.")
        return
    print("Open Replit Bounties:\n")
    for i, bounty in enumerate(bounties, 1):
        print(f"Bounty #{i}")
        print(f"Title      : {bounty.get('title', 'N/A')}")
        print(f"Link       : {bounty.get('link', 'N/A')}")
        print(f"Value      : {bounty.get('value', 'N/A')}")
        print(f"Posted Time: {bounty.get('posted_time', 'N/A')}")
        print("-" * 40)

def get_bounties():
    """
    Returns a dict: {"bounties": [...]} or {"error": ...}
    Tries Firecrawl first, then Playwright if available.
    """
    import json
    try:
        result = app.extract([REPLIT_BOUNTIES_URL], prompt=extract_prompt)
        bounties = getattr(result.data, 'bounties', None)
        if bounties:
            bounties = [b.dict() if hasattr(b, 'dict') else dict(b) for b in bounties]
            return {"bounties": bounties}
    except Exception as e:
        firecrawl_error = str(e)
    try:
        scrape_result = app.scrape_url(REPLIT_BOUNTIES_URL, formats=['json'], json_options={"prompt": extract_prompt})
        bounties = None
        if hasattr(scrape_result, 'json') and scrape_result.json:
            bounties = scrape_result.json.get('bounties', None)
        if bounties:
            return {"bounties": bounties}
    except Exception as e:
        firecrawl_error = str(e)
    if async_playwright:
        try:
            return asyncio.run(_get_bounties_with_playwright())
        except Exception as e:
            return {"error": f"Playwright failed: {e}"}
    return {"error": f"Firecrawl failed: {firecrawl_error if 'firecrawl_error' in locals() else 'Unknown error'} and Playwright not available."}

async def _get_bounties_with_playwright():
    if not async_playwright:
        return {"error": "Playwright is not available. Please install it."}
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(REPLIT_BOUNTIES_URL)
        await page.wait_for_timeout(5000)
        bounty_cards = await page.query_selector_all('[data-cy="bounty-card"]')
        bounties = []
        for card in bounty_cards:
            title = await card.query_selector_eval('[data-cy="bounty-title"]', 'el => el.textContent') if await card.query_selector('[data-cy="bounty-title"]') else 'N/A'
            link = await card.query_selector_eval('a', 'el => el.href') if await card.query_selector('a') else 'N/A'
            value = await card.query_selector_eval('[data-cy="bounty-reward"]', 'el => el.textContent') if await card.query_selector('[data-cy="bounty-reward"]') else 'N/A'
            posted_time = await card.query_selector_eval('[data-cy="bounty-posted-time"]', 'el => el.textContent') if await card.query_selector('[data-cy="bounty-posted-time"]') else 'N/A'
            bounties.append({
                'title': title.strip() if title else 'N/A',
                'link': link.strip() if link else 'N/A',
                'value': value.strip() if value else 'N/A',
                'posted_time': posted_time.strip() if posted_time else 'N/A',
            })
        await browser.close()
        return {"bounties": bounties}

def scrape_with_playwright():
    """
    Runs the Playwright-based scraping and prints the bounties.
    """
    if not async_playwright:
        print("Playwright is not available. Please install it.")
        return
    result = asyncio.run(_get_bounties_with_playwright())
    if "bounties" in result and result["bounties"]:
        print_bounties(result["bounties"])
    elif "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("No bounties found or extraction failed.")

def get_response():
    """
    Returns a string summary of the open bounties or an error message.
    """
    result = get_bounties()
    if "bounties" in result and result["bounties"]:
        bounties = result["bounties"]
        lines = ["Open Replit Bounties:"]
        for i, bounty in enumerate(bounties, 1):
            lines.append(f"Bounty #{i}")
            lines.append(f"Title      : {bounty.get('title', 'N/A')}")
            lines.append(f"Link       : {bounty.get('link', 'N/A')}")
            lines.append(f"Value      : {bounty.get('value', 'N/A')}")
            lines.append(f"Posted Time: {bounty.get('posted_time', 'N/A')}")
            lines.append("-" * 40)
        return "\n".join(lines)
    elif "error" in result:
        return f"Error: {result['error']}"
    else:
        return "No bounties found or extraction failed."

def try_firecrawl():
    """
    Tries Firecrawl extraction and prints bounties if found. Returns True if successful, else False.
    """
    result = get_bounties()
    if "bounties" in result and result["bounties"]:
        print_bounties(result["bounties"])
        return True
    return False

def main():
    print("Trying Firecrawl extraction...")
    if not try_firecrawl():
        print("\nFalling back to Playwright scraping...")
        if not async_playwright:
            print("Playwright is not available. Please install it.")
            return
        asyncio.run(scrape_with_playwright())

if __name__ == "__main__":
    main()