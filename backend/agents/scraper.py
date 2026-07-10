import logging
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)

async def scrape_jobs(search_query: str = "software engineer"):
    """
    Stealthy Playwright scraper to extract job postings.
    Uses playwright-stealth to bypass basic bot detections.
    """
    logger.info(f"Starting Scraper Agent for query: {search_query}")
    
    postings = []
    
    async with async_playwright() as p:
        # Launch browser in headless mode but with standard viewport/agent
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        # Apply stealth config to mask headless artifacts
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        try:
            # Target LinkedIn's public jobs page (no login required for search)
            encoded_query = search_query.replace(" ", "%20")
            target_url = f"https://www.linkedin.com/jobs/search?keywords={encoded_query}&location=United%20States&f_TPR=r86400"
            
            logger.info(f"Navigating to {target_url}")
            await page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
            
            # Scroll down slightly to trigger lazy loads
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(2)
            
            # Wait for job cards to render
            await page.wait_for_selector(".job-search-card", timeout=15000)
            
            # Extract basic details from the cards
            cards = await page.query_selector_all(".job-search-card")
            logger.info(f"Found {len(cards)} job cards. Extracting top 5...")
            
            for card in cards[:5]:
                title_elem = await card.query_selector(".base-search-card__title")
                company_elem = await card.query_selector(".base-search-card__subtitle")
                link_elem = await card.query_selector(".base-card__full-link")
                
                title = await title_elem.inner_text() if title_elem else "Unknown Title"
                company = await company_elem.inner_text() if company_elem else "Unknown Company"
                link = await link_elem.get_attribute("href") if link_elem else ""
                
                postings.append({
                    "title": title.strip(),
                    "company": company.strip(),
                    "link": link.strip(),
                    "source": "LinkedIn"
                })
                
        except Exception as e:
            logger.error(f"Scraping error encountered: {e}")
        finally:
            await browser.close()
            
    return postings

# For standalone testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = asyncio.run(scrape_jobs("machine learning engineer"))
    for r in res:
        print(r)
