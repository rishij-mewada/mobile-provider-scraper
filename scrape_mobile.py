 
import pandas as pd
from playwright.sync_api import sync_playwright
import time
import random
from datetime import datetime
import os
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_browser(playwright):
    """Configure browser for GitHub Actions environment"""
    browser = playwright.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    )
    return browser, context

def extract_price(text):
    """Extract numeric price from text"""
    if not text:
        return None
    # Look for price patterns like $50, $50/mo, $50.00
    price_match = re.search(r'\$(\d+(?:\.\d{2})?)', str(text))
    if price_match:
        return float(price_match.group(1))
    return None

def scrape_verizon(page):
    """Scrape Verizon pricing data"""
    try:
        logger.info("Scraping Verizon...")
        page.goto("https://www.verizon.com/plans/unlimited/", wait_until='networkidle', timeout=30000)
        time.sleep(5)
        
        plans_data = []
        
        # Try multiple selectors for Verizon plans
        plan_selectors = [
            '[data-testid*="plan"]',
            '.plan-card',
            '.unlimited-plan',
            '.plan-container',
            '.plan-tile'
        ]
        
        plan_elements = []
        for selector in plan_selectors:
            elements = page.query_selector_all(selector)
            if elements:
                plan_elements = elements
                logger.info(f"Found {len(elements)} plans using selector: {selector}")
                break
        
        if not plan_elements:
            logger.warning("No plan elements found on Verizon page")
            return []
        
        for i, plan_element in enumerate(plan_elements[:5]):  # Limit to 5 plans
            try:
                # Extract plan name
                plan_name_selectors = ['h2', 'h3', '.plan-name', '.plan-title', '[data-testid*="title"]']
                plan_name = "Unknown Plan"
                
                for selector in plan_name_selectors:
                    name_elem = plan_element.query_selector(selector)
                    if name_elem:
                        plan_name = name_elem.inner_text().strip()
                        break
                
                # Extract pricing information
                price_selectors = ['.price', '[data-testid*="price"]', '.cost', '.monthly-price']
                prices = []
                
                for selector in price_selectors:
                    price_elements = plan_element.query_selector_all(selector)
                    for price_elem in price_elements:
                        price_text = price_elem.inner_text()
                        price = extract_price(price_text)
                        if price:
                            prices.append(price)
                
                # Create pricing data structure
                pricing_data = {
                    'provider_name': 'Verizon',
                    'provider_type': 'MNO',
                    'plan_name': plan_name,
                    'price_1_line': prices[0] if len(prices) > 0 else None,
                    'price_2_lines': prices[1] if len(prices) > 1 else None,
                    'price_3_lines': prices[2] if len(prices) > 2 else None,
                    'price_4_lines': prices[3] if len(prices) > 3 else None,
                    'price_5_lines': prices[4] if len(prices) > 4 else None,
                    'autopay_discount': 10,  # Verizon typically offers $10/line autopay discount
                    'taxes_fees_included': 'No',
                    'source_url': page.url
                }
                
                plans_data.append(pricing_data)
                logger.info(f"Extracted Verizon plan: {plan_name}")
                
            except Exception as e:
                logger.warning(f"Error extracting Verizon plan {i}: {e}")
                continue
        
        return plans_data
        
    except Exception as e:
        logger.error(f"Error scraping Verizon: {e}")
        return []

def scrape_tmobile(page):
    """Scrape T-Mobile pricing data"""
    try:
        logger.info("Scraping T-Mobile...")
        page.goto("https://www.t-mobile.com/cell-phone-plans", wait_until='networkidle', timeout=30000)
        time.sleep(5)
        
        plans_data = []
        
        # T-Mobile plan selectors
        plan_selectors = [
            '.plan-tile',
            '[data-testid*="plan"]',
            '.plan-card',
            '.plan-container'
        ]
        
        plan_elements = []
        for selector in plan_selectors:
            elements = page.query_selector_all(selector)
            if elements:
                plan_elements = elements
                logger.info(f"Found {len(elements)} T-Mobile plans using selector: {selector}")
                break
        
        if not plan_elements:
            logger.warning("No plan elements found on T-Mobile page")
            return []
        
        for i, plan_element in enumerate(plan_elements[:5]):
            try:
                # Extract plan name
                plan_name_selectors = ['h2', 'h3', '.plan-title', '.plan-name']
                plan_name = "Unknown Plan"
                
                for selector in plan_name_selectors:
                    name_elem = plan_element.query_selector(selector)
                    if name_elem:
                        plan_name = name_elem.inner_text().strip()
                        break
                
                # Extract pricing
                price_selectors = ['.price', '.cost', '[data-testid*="price"]']
                prices = []
                
                for selector in price_selectors:
                    price_elements = plan_element.query_selector_all(selector)
                    for price_elem in price_elements:
                        price_text = price_elem.inner_text()
                        price = extract_price(price_text)
                        if price:
                            prices.append(price)
                
                pricing_data = {
                    'provider_name': 'T-Mobile',
                    'provider_type': 'MNO',
                    'plan_name': plan_name,
                    'price_1_line': prices[0] if len(prices) > 0 else None,
                    'price_2_lines': prices[1] if len(prices) > 1 else None,
                    'price_3_lines': prices[2] if len(prices) > 2 else None,
                    'price_4_lines': prices[3] if len(prices) > 3 else None,
                    'price_5_lines': prices[4] if len(prices) > 4 else None,
                    'autopay_discount': 5,  # T-Mobile typically offers $5/line autopay discount
                    'taxes_fees_included': 'Yes',
                    'source_url': page.url
                }
                
                plans_data.append(pricing_data)
                logger.info(f"Extracted T-Mobile plan: {plan_name}")
                
            except Exception as e:
                logger.warning(f"Error extracting T-Mobile plan {i}: {e}")
                continue
        
        return plans_data
        
    except Exception as e:
        logger.error(f"Error scraping T-Mobile: {e}")
        return []

def convert_to_tableau_format(all_data):
    """Convert scraped data to Tableau-friendly format"""
    tableau_rows = []
    
    for provider_data in all_data:
        # Create one row per line count (normalized format)
        for line_count in range(1, 6):
            price_key = f'price_{line_count}_line{"s" if line_count > 1 else ""}'
            
            if provider_data.get(price_key):
                row = {
                    'extraction_date': datetime.now().strftime('%Y-%m-%d'),
                    'extraction_timestamp': datetime.now().isoformat(),
                    'provider_name': provider_data['provider_name'],
                    'provider_type': provider_data['provider_type'],
                    'plan_name': provider_data['plan_name'],
                    'line_count': line_count,
                    'monthly_price': provider_data[price_key],
                    'autopay_discount_amount': provider_data.get('autopay_discount', 0) or 0,
                    'has_autopay_discount': bool(provider_data.get('autopay_discount')),
                    'taxes_fees_included': provider_data.get('taxes_fees_included', 'No'),
                    'price_per_line': provider_data[price_key] / line_count,
                    'source_url': provider_data.get('source_url', '')
                }
                tableau_rows.append(row)
    
    return pd.DataFrame(tableau_rows)

def main():
    """Main scraping function"""
    logger.info("Starting mobile provider scraping...")
    
    all_scraped_data = []
    
    with sync_playwright() as playwright:
        browser, context = setup_browser(playwright)
        page = context.new_page()
        
        try:
            # Scrape major providers
            providers_to_scrape = [
                ('Verizon', scrape_verizon),
                ('T-Mobile', scrape_tmobile),
            ]
            
            for provider_name, scrape_function in providers_to_scrape:
                try:
                    logger.info(f"Starting {provider_name} scrape...")
                    data = scrape_function(page)
                    all_scraped_data.extend(data)
                    logger.info(f"Completed {provider_name}: {len(data)} plans extracted")
                    
                    # Random delay between providers
                    time.sleep(random.uniform(3, 7))
                    
                except Exception as e:
                    logger.error(f"Failed to scrape {provider_name}: {e}")
                    continue
            
            # Convert to Tableau format and save
            if all_scraped_data:
                tableau_df = convert_to_tableau_format(all_scraped_data)
                
                # Save with date prefix (matching your LLM scraper format)
                date_str = datetime.now().strftime('%Y%m%d')
                filename = f"{date_str} - Daily Mobile Provider Pricing.csv"
                
                tableau_df.to_csv(filename, index=False)
                logger.info(f"Saved {len(tableau_df)} records to {filename}")
                
                # Also save archive copy
                archive_filename = f"{date_str} - Daily Mobile Provider Pricing - Archive.csv"
                tableau_df.to_csv(archive_filename, index=False)
                logger.info(f"Archive saved as {archive_filename}")
                
            else:
                logger.warning("No data scraped from any provider")
                
        finally:
            browser.close()

if __name__ == "__main__":
    main()
