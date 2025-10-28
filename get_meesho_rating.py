#!/usr/bin/env python3
"""
Simple script to get rating from Meesho page
"""

import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def get_rating_from_page(url):
    """Get rating and review info from Meesho page"""
    
    print(f"Getting data from: {url}")
    
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    
    driver = uc.Chrome(options=options)
    
    try:
        driver.get(url)
        time.sleep(8)  # Wait for page to fully load
        
        print("\nSearching for rating information...")
        
        # Try to find any element with rating-like text
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        
        # Look for rating pattern in page text
        rating_pattern = r'(\d+\.\d+)'
        rating_match = re.search(rating_pattern, page_text)
        
        result = {
            'rating': None,
            'ratings_count': None,
            'reviews_count': None
        }
        
        # Extract rating number
        if rating_match:
            rating_num = rating_match.group(1)
            try:
                rating_value = float(rating_num)
                if 0 <= rating_value <= 5:
                    result['rating'] = f"{rating_num}*"
                    print(f"Rating found: {result['rating']}")
            except:
                pass
        
        # Extract ratings count
        ratings_match = re.search(r'([\d,]+)\s+[Rr]atings?', page_text)
        if ratings_match:
            ratings_num = ratings_match.group(1).replace(',', '')
            result['ratings_count'] = f"{ratings_num} Ratings"
            print(f"Ratings count: {result['ratings_count']}")
        
        # Extract reviews count
        reviews_match = re.search(r'([\d,]+)\s+[Rr]eviews?', page_text)
        if reviews_match:
            reviews_num = reviews_match.group(1).replace(',', '')
            result['reviews_count'] = f"{reviews_num} Reviews"
            print(f"Reviews count: {result['reviews_count']}")
        
        print("\n" + "="*80)
        print("EXTRACTION RESULT:")
        print("="*80)
        print(f"Rating: {result['rating'] or 'Not found'}")
        print(f"Ratings Count: {result['ratings_count'] or 'Not found'}")
        print(f"Reviews Count: {result['reviews_count'] or 'Not found'}")
        print("="*80)
        
        return result
        
    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://www.meesho.com/casual-polyester-blend-ribbed-collar-v-neck-regular-long-sleeves-stylish-coffee-top-20inches/p/71ldyd"
    
    result = get_rating_from_page(url)
    
    print("\nJSON Output:")
    import json
    print(json.dumps(result, indent=2))

