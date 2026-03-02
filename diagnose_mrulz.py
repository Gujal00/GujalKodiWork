#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnostic script to inspect current HTML structure of mrulz website
Helps identify the correct CSS selectors for scraping
"""

import requests
from bs4 import BeautifulSoup


def diagnose_mrulz_structure():
    """Inspect the actual HTML structure of the website"""
    url = 'https://www.5movierulz.travel/category/tamil-movie/'
    
    print("\n" + "="*70)
    print("Diagnosing Movie Rulz Website Structure")
    print("="*70)
    print(f"URL: {url}\n")
    
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try common container selectors
        print("[1] Looking for common container selectors...\n")
        
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
        print("\n[2] Looking for movie item selectors...\n")
        
        item_selectors = [
            ('div.boxed.film', soup.find_all('div', {'class': 'boxed film'})),
            ('div.film', soup.find_all('div', {'class': 'film'})),
            ('article', soup.find_all('article')),
            ('div.post', soup.find_all('div', {'class': 'post'})),
            ('div.movie', soup.find_all('div', {'class': 'movie'})),
            ('li', soup.find_all('li')[:5]),  # Sample first 5
        ]
        
        for selector, items in item_selectors:
            if items:
                print(f"✓ Found {len(items)} items with: {selector}")
                # Show first item structure
                if items[0]:
                    print(f"  Sample HTML: {str(items[0])[:150]}...")
                    # Check for links
                    link = items[0].find('a')
                    if link:
                        print(f"  Link found: href={link.get('href')}")
                    # Check for images
                    img = items[0].find('img')
                    if img:
                        print(f"  Image found: src={img.get('src')}")
            else:
                print(f"✗ Not found: {selector}")
        
        # Show actual page structure
        print("\n[3] Page structure summary:\n")
        body = soup.find('body')
        if body:
            # Get main divs in body
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
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Parse error: {str(e)}")
        return False


if __name__ == '__main__':
    diagnose_mrulz_structure()
