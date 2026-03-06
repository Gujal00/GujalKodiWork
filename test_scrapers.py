#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for Movie Rulz scraper using Selenium
Validates that scraper endpoints are reachable and have expected HTML structure
Uses Selenium for headless browser automation to bypass SSL/WAF blocks
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time


def test_mrulz_endpoint():
    """Test if mrulz endpoint is reachable and has expected structure using Selenium"""
    url = 'https://www.5movierulz.claims/category/tamil-movie/'
    
    print("\n" + "="*60)
    print("Testing Movie Rulz Scraper (Selenium)")
    print("="*60)
    print(f"URL: {url}")
    
    driver = None
    try:
        # Setup Chrome options
        print("\n[1/4] Initializing headless browser...")
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✓ Browser initialized")
        
        # Navigate to page
        print("\n[2/4] Loading webpage...")
        driver.get(url)
        print("✓ Page loaded")
        
        # Wait for content to load
        print("\n[3/4] Waiting for content to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.boxed.film"))
        )
        print("✓ Content loaded")
        
        # Parse HTML with BeautifulSoup
        print("\n[4/4] Parsing page structure...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.find_all('div', {'class': 'boxed film'})
        
        if not items:
            print("✗ FAILED: No movies found")
            return False
        
        print(f"✓ Found {len(items)} movies on the page")
        
        # Verify movie links
        valid_links = 0
        for item in items[:3]:
            link = item.find('a')
            if link and link.get('href'):
                valid_links += 1
        
        if valid_links > 0:
            print(f"✓ Found valid movie links ({valid_links} verified)")
            print(f"\nSample movie title: {items[0].text.strip()[:60]}...")
            print("\n" + "="*60)
            print("✓ SUCCESS: Movie Rulz scraper is working!")
            print("="*60)
            return True
        else:
            print("✗ FAILED: No valid movie links found")
            return False
            
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False
    finally:
        if driver:
            driver.quit()
            print("\n✓ Browser closed")


if __name__ == '__main__':
    test_mrulz_endpoint()
