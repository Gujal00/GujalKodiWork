#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for Deccan Delight scrapers
Validates that scraper endpoints are reachable and have expected HTML structure
"""

import requests
from bs4 import BeautifulSoup, SoupStrainer


def test_mrulz_endpoint():
    """Test if mrulz endpoint is reachable and has expected structure"""
    url = 'https://www.5movierulz.travel/category/tamil-movie/'
    
    print("\n" + "="*60)
    print("Testing Movie Rulz Scraper")
    print("="*60)
    print(f"URL: {url}")
    
    try:
        # Test connectivity
        print("\n[1/3] Testing endpoint connectivity...")
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        print("✓ Endpoint is reachable")
        
        # Check if HTML has expected container
        print("\n[2/3] Checking HTML structure...")
        mlink = SoupStrainer('div', {'id': 'content'})
        mdiv = BeautifulSoup(response.text, "html.parser", parse_only=mlink)
        items = mdiv.find_all('div', {'class': 'boxed film'})
        
        if not items:
            print("✗ FAILED: No movies found - HTML structure may have changed")
            print("  Expected to find: <div id='content'> with <div class='boxed film'>")
            return False
        
        print(f"✓ Found {len(items)} movies on the page")
        
        # Verify movie links
        print("\n[3/3] Validating movie links...")
        valid_links = 0
        for item in items[:3]:  # Check first 3 items
            link_elem = item.find('a')
            if link_elem and link_elem.get('href'):
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
            
    except requests.exceptions.Timeout:
        print("✗ FAILED: Request timed out - endpoint may be down")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ FAILED: Cannot connect to endpoint - check internet or endpoint URL")
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ FAILED: Request error - {str(e)}")
        return False
    except Exception as e:
        print(f"✗ FAILED: Error parsing HTML - {str(e)}")
        return False


if __name__ == '__main__':
    test_mrulz_endpoint()
