#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnostic script to inspect Movie Rulz website using Selenium
Helps identify the correct CSS selectors for scraping
Uses Selenium for headless browser automation to bypass SSL/WAF blocks
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time


def diagnose_mrulz_structure():
    """Inspect the HTML structure of the website using Selenium"""
    url = 'https://www.5movierulz.travel/category/tamil-movie/'
    
    print("\n" + "="*70)
    print("Diagnosing Movie Rulz Website Structure (Selenium)")
    print("="*70)
    print(f"URL: {url}\n")
    
    driver = None
    try:
        # Setup Chrome options
        print("[1] Initializing headless browser...")
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✓ Browser initialized\n")
        
        # Navigate to page
        print("[2] Loading webpage...")
        driver.get(url)
        time.sleep(3)  # Wait for content to load
        print("✓ Page loaded\n")
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Try common container selectors
        print("[3] Looking for common container selectors...\n")
        
        containers = [
            ('div[id="container"]', soup.find('div', {'id': 'container'})),
            ('div[id="content"]', soup.find('div', {'id': 'content'})),
            ('div[class="container"]', soup.find('div', {'class': 'container'})),
            ('main', soup.find('main')),
            ('article', soup.find('article')),
        ]
        
        for selector, element in containers:
            if element:
                print(f"✓ Found: {selector}")
                print(f"  Tag: {element.name}, ID: {element.get('id')}, Class: {element.get('class')}")
            else:
                print(f"✗ Not found: {selector}")
        
        # Try common item selectors
        print("\n[4] Looking for movie item selectors...\n")
        
        item_selectors = [
            ('div.boxed.film', soup.find_all('div', {'class': 'boxed film'})),
            ('div.film', soup.find_all('div', {'class': 'film'})),
            ('article', soup.find_all('article')),
            ('div.post', soup.find_all('div', {'class': 'post'})),
            ('div.movie', soup.find_all('div', {'class': 'movie'})),
            ('li', soup.find_all('li')[:5]),
        ]
        
        for selector, items in item_selectors:
            if items:
                print(f"✓ Found {len(items)} items with: {selector}")
                if items[0]:
                    print(f"  Sample HTML: {str(items[0])[:150]}...")
                    link = items[0].find('a')
                    if link:
                        print(f"  Link found: href={link.get('href')}")
                    img = items[0].find('img')
                    if img:
                        print(f"  Image found: src={img.get('src')}")
            else:
                print(f"✗ Not found: {selector}")
        
        # Show actual page structure
        print("\n[5] Page structure summary:\n")
        body = soup.find('body')
        if body:
            main_divs = body.find_all('div', recursive=False)
            print(f"Direct div children in body: {len(main_divs)}")
            for i, div in enumerate(main_divs[:3]):
                print(f"  [{i}] id={div.get('id')}, class={div.get('class')}")
        
        print("\n" + "="*70)
        print("RECOMMENDATION:")
        print("Based on the findings above, update the scraper's selectors:")
        print("- Change 'div[id=\"container\"]' to the correct container")
        print("- Change 'div[class=\"boxed film\"]' to the correct item selector")
        print("="*70)
        
        return True
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False
    finally:
        if driver:
            driver.quit()
            print("\n✓ Browser closed")


if __name__ == '__main__':
    diagnose_mrulz_structure()
