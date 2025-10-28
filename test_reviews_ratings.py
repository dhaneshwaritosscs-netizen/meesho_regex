#!/usr/bin/env python3
"""
Test script for reviews and ratings extraction
"""

import json
from inference import generate_reviews_json, extract_reviews_ratings

def test_reviews_ratings():
    """Test reviews and ratings extraction"""
    
    print("=" * 80)
    print("REVIEWS AND RATINGS EXTRACTION TEST")
    print("=" * 80)
    
    test_cases = [
        {
            'name': 'Meesho Product Example',
            'rating': '4.2★',
            'rating_count': '20596 Ratings',
            'rating_count_raw': '9777 Reviews',
            'expected': {
                'Rating': '4.2★',
                'Rating_Count': '20596 Ratings',
                'Review_Count': '9777 Reviews'
            }
        },
        {
            'name': 'High Rating Product',
            'rating': '4.8★',
            'rating_count': '12450 Ratings',
            'rating_count_raw': '8650 Reviews',
            'expected': {
                'Rating': '4.8★',
                'Rating_Count': '12450 Ratings',
                'Review_Count': '8650 Reviews'
            }
        },
        {
            'name': 'Medium Rating Product',
            'rating': '3.5★',
            'rating_count': '8500 Ratings',
            'rating_count_raw': '5200 Reviews',
            'expected': {
                'Rating': '3.5★',
                'Rating_Count': '8500 Ratings',
                'Review_Count': '5200 Reviews'
            }
        }
    ]
    
    print("\n" + "=" * 80)
    print("TESTING GENERATE_REVIEWS_JSON")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['name']}")
        print("-" * 80)
        
        # Build input text
        input_text = ""
        if test_case.get('rating'):
            input_text += f"Rating: \"{test_case['rating']}\" "
        if test_case.get('rating_count'):
            input_text += f"Rating Count: \"{test_case['rating_count']}\" "
        if test_case.get('rating_count_raw'):
            # Note: rating_count_raw is actually Review_Count
            input_text += f"Review Count: \"{test_case['rating_count_raw']}\""
        
        print(f"Input: {input_text}")
        print(f"Expected Output: {json.dumps(test_case['expected'], indent=2)}")
        
        # Test extraction
        result = generate_reviews_json(input_text)
        
        print(f"Actual Result: {json.dumps(result, indent=2)}")
        
        if 'json' in result:
            extracted = result['json']
            print("\n✅ Extraction successful!")
            
            # Validate against expected
            for key, expected_value in test_case['expected'].items():
                actual_value = extracted.get(key)
                if actual_value == expected_value:
                    print(f"  ✅ {key}: {actual_value}")
                else:
                    print(f"  ❌ {key}: Expected '{expected_value}', got '{actual_value}'")
        else:
            print("\n❌ Extraction failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("TESTING EXTRACT_REVIEWS_RATINGS")
    print("=" * 80)
    
    # Test with product data
    product_data = {
        'name': 'Casual Polyester Blend Coffee Top',
        'price': '₹197',
        'rating': '4.2★',
        'rating_count': '20596 Ratings, 9777 Reviews'
    }
    
    print(f"\nInput Product Data:")
    print(json.dumps(product_data, indent=2))
    
    print("\nExtracting reviews and ratings...")
    result = extract_reviews_ratings(product_data)
    
    print(f"\nExtracted Result:")
    print(json.dumps(result, indent=2))
    
    if 'rating' in result and 'rating_count' in result:
        print("\n✅ Reviews and ratings extracted successfully!")
    else:
        print("\n❌ Reviews and ratings extraction failed!")
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED!")
    print("=" * 80)

if __name__ == "__main__":
    test_reviews_ratings()

