#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Flask app for extracting ratings and reviews from Meesho URLs
"""

import sys
import io
import os

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

from flask import Flask, render_template, request, jsonify
import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Meesho Rating & Reviews Extractor</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                width: 100%;
                max-width: 600px;
                padding: 40px;
            }
            
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }
            
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }
            
            .input-group {
                margin-bottom: 25px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
            }
            
            input[type="text"] {
                width: 100%;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 16px;
                transition: all 0.3s;
            }
            
            input[type="text"]:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            button {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
            }
            
            button:hover {
                transform: translateY(-2px);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            
            .loading {
                text-align: center;
                padding: 20px;
                color: #667eea;
            }
            
            .results {
                margin-top: 30px;
                padding: 25px;
                background: #f8f9fa;
                border-radius: 15px;
                display: none;
            }
            
            .result-item {
                padding: 15px;
                margin-bottom: 15px;
                background: white;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            
            .result-label {
                font-weight: 600;
                color: #666;
                font-size: 14px;
                margin-bottom: 5px;
            }
            
            .result-value {
                font-size: 20px;
                color: #333;
                font-weight: 600;
            }
            
            .error {
                background: #fee;
                border-left-color: #f44;
                color: #c33;
            }
            
            .success {
                background: #efe;
                border-left-color: #4a4;
                color: #363;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌟 Meesho Rating Extractor</h1>
            <p class="subtitle">Extract ratings and reviews from any Meesho product URL</p>
            
            <form id="extractForm">
                <div class="input-group">
                    <label for="url">Meesho Product URL:</label>
                    <input 
                        type="text" 
                        id="url" 
                        name="url" 
                        placeholder="https://www.meesho.com/..."
                        required
                    >
                </div>
                
                <button type="submit" id="submitBtn">Extract Ratings & Reviews</button>
            </form>
            
            <div id="loading" class="loading" style="display: none;">
                <div class="spinner"></div>
                <p>Loading product page...</p>
            </div>
            
            <div id="results" class="results"></div>
        </div>
        
        <script>
            document.getElementById('extractForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const url = document.getElementById('url').value;
                const submitBtn = document.getElementById('submitBtn');
                const loading = document.getElementById('loading');
                const resultsDiv = document.getElementById('results');
                
                // Show loading, hide results
                loading.style.display = 'block';
                resultsDiv.style.display = 'none';
                submitBtn.disabled = true;
                submitBtn.textContent = 'Extracting...';
                
                try {
                    const response = await fetch('/extract', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ url: url })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        // Display results
                        let html = '<div class="result-item success"><div class="result-label">✅ Success</div></div>';
                        
                        if (data.rating) {
                            html += `<div class="result-item">
                                <div class="result-label">Rating</div>
                                <div class="result-value">${data.rating}</div>
                            </div>`;
                        }
                        
                        if (data.ratings_count) {
                            html += `<div class="result-item">
                                <div class="result-label">Ratings Count</div>
                                <div class="result-value">${data.ratings_count}</div>
                            </div>`;
                        }
                        
                        if (data.reviews_count) {
                            html += `<div class="result-item">
                                <div class="result-label">Reviews Count</div>
                                <div class="result-value">${data.reviews_count}</div>
                            </div>`;
                        }
                        
                        resultsDiv.innerHTML = html;
                    } else {
                        // Show error
                        resultsDiv.innerHTML = `
                            <div class="result-item error">
                                <div class="result-label">❌ Error</div>
                                <div class="result-value">${data.error || 'Failed to extract data'}</div>
                            </div>
                        `;
                    }
                    
                    resultsDiv.style.display = 'block';
                } catch (error) {
                    resultsDiv.innerHTML = `
                        <div class="result-item error">
                            <div class="result-label">❌ Error</div>
                            <div class="result-value">${error.message}</div>
                        </div>
                    `;
                    resultsDiv.style.display = 'block';
                } finally {
                    loading.style.display = 'none';
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Extract Ratings & Reviews';
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/extract', methods=['POST'])
def extract_ratings():
    """Extract ratings and reviews from Meesho URL"""
    try:
        data = request.json
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'})
        
        print(f"\n[INFO] Extracting from: {url}")
        
        # Setup browser
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        # Remove headless mode temporarily for debugging
        # options.add_argument("--headless")  # Run in background
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = uc.Chrome(options=options)
        
        try:
            print(f"[INFO] Navigating to URL...")
            driver.get(url)
            
            # Wait longer for dynamic content
            print(f"[INFO] Waiting for page to load...")
            time.sleep(12)  # Increased wait time
            
            # Get page text
            print(f"[INFO] Extracting page content...")
            page_text = driver.find_element(By.TAG_NAME, 'body').text
            
            print(f"[INFO] Page text length: {len(page_text)} characters")
            
            # Debug: print first 500 characters
            try:
                print(f"[DEBUG] First 500 chars: {page_text[:500]}")
            except UnicodeEncodeError:
                print(f"[DEBUG] First 500 chars: (contains unicode characters)")
            
            result = {
                'success': False,
                'rating': None,
                'ratings_count': None,
                'reviews_count': None
            }
            
            # Extract rating - multiple patterns
            rating_patterns = [
                r'(\d+\.\d+)\s*\*',  # 4.2*
                r'(\d+\.\d+)',  # Just number
                r'Rating:\s*(\d+\.\d+)',  # Rating: 4.2
            ]
            
            for pattern in rating_patterns:
                rating_match = re.search(pattern, page_text)
                if rating_match:
                    rating_num = rating_match.group(1)
                    try:
                        rating_value = float(rating_num)
                        if 0 <= rating_value <= 5:
                            result['rating'] = f"{rating_num}★"
                            print(f"[OK] Rating: {result['rating']}")
                            break
                    except:
                        pass
            
            # Extract ratings count - multiple patterns
            ratings_patterns = [
                r'([\d,]+)\s+[Rr]atings?',
                r'([\d,]+\s*[Rr]atings?)',
            ]
            
            for pattern in ratings_patterns:
                ratings_match = re.search(pattern, page_text)
                if ratings_match:
                    ratings_full = ratings_match.group(1)
                    # Extract numbers
                    numbers = re.findall(r'[\d,]+', ratings_full)
                    if numbers:
                        ratings_num = numbers[0].replace(',', '')
                        result['ratings_count'] = f"{ratings_num} Ratings"
                        print(f"[OK] Ratings count: {result['ratings_count']}")
                        break
            
            # Extract reviews count
            reviews_match = re.search(r'([\d,]+)\s+[Rr]eviews?', page_text)
            if reviews_match:
                reviews_num = reviews_match.group(1).replace(',', '')
                result['reviews_count'] = f"{reviews_num} Reviews"
                print(f"[OK] Reviews count: {result['reviews_count']}")
            
            # Check if we got any data
            if result['rating'] or result['ratings_count'] or result['reviews_count']:
                result['success'] = True
                print(f"[SUCCESS] Data extracted successfully")
            else:
                result['error'] = 'No rating or review data found on the page'
                print(f"[ERROR] No data found")
            
            return jsonify(result)
            
        finally:
            driver.quit()
            
    except Exception as e:
        error_msg = str(e)
        # Handle Unicode errors in error messages
        try:
            print(f"[ERROR] {error_msg}")
        except UnicodeEncodeError:
            print(f"[ERROR] {error_msg.encode('ascii', 'ignore').decode('ascii')}")
        
        # Return safe error message
        safe_error = error_msg.encode('ascii', 'ignore').decode('ascii')
        return jsonify({
            'success': False,
            'error': f'Failed to extract data: {safe_error}'
        })

if __name__ == '__main__':
    print("="*80)
    print("Meesho Rating & Reviews Extractor")
    print("="*80)
    print("Starting Flask server on http://localhost:5001")
    print("Open your browser and go to http://localhost:5001")
    print("="*80)
    app.run(debug=True, host='0.0.0.0', port=5001)

