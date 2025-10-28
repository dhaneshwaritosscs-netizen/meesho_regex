#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple ratings and reviews extractor using regex patterns
No scraping, no LLM model needed
"""

import sys
import io

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

import re

def extract_rating_reviews(text):
    """Extract rating and reviews from text using regex patterns"""
    
    result = {
        'rating': None,
        'rating_count': None,
        'review_count': None
    }
    
    print(f"[INFO] Extracting from text: {text[:100]}...")
    
    # Extract rating pattern (e.g., 4.2★, 4.2, 4.2*, etc.)
    rating_patterns = [
        r'(\d+\.\d+)\s*\*+',  # 4.2***
        r'(\d+\.\d+)\s*★+',   # 4.2★
        r'rating[:\s]+(\d+\.\d+)',  # rating: 4.2
        r'(\d+\.\d+)',  # Just the number
    ]
    
    for pattern in rating_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            rating_num = match.group(1)
            try:
                rating_value = float(rating_num)
                if 0 <= rating_value <= 5:
                    result['rating'] = f"{rating_num}★"
                    print(f"[OK] Rating: {result['rating']}")
                    break
            except:
                pass
    
    # Extract ratings count
    ratings_patterns = [
        r'([\d,]+)\s*ratings?',
        r'rating[:\s]+([\d,]+)',
        r'(\d+[,\.]?\d*)\s*ratings?',
    ]
    
    for pattern in ratings_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            ratings_num = match.group(1).replace(',', '').replace('.', '')
            result['rating_count'] = f"{ratings_num} Ratings"
            print(f"[OK] Rating Count: {result['rating_count']}")
            break
    
    # Extract reviews count
    reviews_patterns = [
        r'([\d,]+)\s*reviews?',
        r'review[:\s]+([\d,]+)',
        r'(\d+[,\.]?\d*)\s*reviews?',
    ]
    
    for pattern in reviews_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            reviews_num = match.group(1).replace(',', '').replace('.', '')
            result['review_count'] = f"{reviews_num} Reviews"
            print(f"[OK] Review Count: {result['review_count']}")
            break
    
    return result

# Test examples
if __name__ == "__main__":
    test_cases = [
        "Rating: 4.2★ Rating Count: 20596 Ratings Review Count: 9777 Reviews",
        "4.2★ 20596 Ratings, 9777 Reviews",
        "Product has 4.5 star rating with 10000 ratings and 5000 reviews",
        "Rating: 4.8★ 12450 Ratings 8650 Reviews",
    ]
    
    print("="*80)
    print("SIMPLE RATING & REVIEWS EXTRACTOR")
    print("="*80)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input: {text}")
        result = extract_rating_reviews(text)
        print(f"Result:")
        print(f"  Rating: {result['rating']}")
        print(f"  Rating Count: {result['rating_count']}")
        print(f"  Review Count: {result['review_count']}")
        print("-"*80)

