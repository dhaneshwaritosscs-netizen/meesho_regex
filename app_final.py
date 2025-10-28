#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Flask app for extracting ratings and reviews
NO SCRAPING - Uses regex patterns to extract from text
"""

import sys
import io

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

from flask import Flask, request, jsonify
import re
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

app = Flask(__name__)

def extract_rating_reviews(text):
    """Extract rating and reviews from text using regex patterns"""
    
    result = {
        'rating': None,
        'rating_count': None,
        'review_count': None
    }
    
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
                    break
            except:
                pass
    
    # Extract ratings count
    ratings_patterns = [
        r'([\d,]+)\s*ratings?',
        r'rating\s+count[:\s]+([\d,]+)',
        r'(\d+[,\.]?\d*)\s*ratings?',
    ]
    
    for pattern in ratings_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            ratings_num = match.group(1).replace(',', '').replace('.', '')
            result['rating_count'] = f"{ratings_num} Ratings"
            break
    
    # Extract reviews count
    reviews_patterns = [
        r'([\d,]+)\s*reviews?',
        r'review\s+count[:\s]+([\d,]+)',
        r'(\d+[,\.]?\d*)\s*reviews?',
    ]
    
    for pattern in reviews_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            reviews_num = match.group(1).replace(',', '').replace('.', '')
            result['review_count'] = f"{reviews_num} Reviews"
            break
    
    return result

@app.route('/')
def index():
    with open('app_final_chat_ui.html', 'r', encoding='utf-8') as f:
        return f.read()

def old_index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>URL Data Extractor</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
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
                max-width: 700px;
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
            
            .info-box {
                background: #f0f4ff;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 5px;
                font-size: 14px;
                color: #555;
            }
            
            .input-group { margin-bottom: 25px; }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
            }
            
            textarea {
                width: 100%;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 16px;
                font-family: inherit;
                resize: vertical;
                min-height: 150px;
                transition: all 0.3s;
            }
            
            textarea:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .example {
                background: #f9f9f9;
                padding: 15px;
                border-radius: 8px;
                margin-top: 10px;
                font-size: 13px;
                color: #666;
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
            
            button:hover { transform: translateY(-2px); }
            button:disabled { opacity: 0.6; cursor: not-allowed; }
            
            .loading {
                text-align: center;
                padding: 20px;
                display: none;
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
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
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
            
            .error { background: #fee; border-left-color: #f44; color: #c33; }
            .success { background: #efe; border-left-color: #4a4; }
            
            .url-result { margin-top: 20px; border: 2px solid #667eea; border-radius: 15px; overflow: hidden; }
            .url-header { background: #667eea; color: white; padding: 15px; font-weight: 600; word-break: break-all; }
            .url-content { padding: 15px; }
            .processing { background: #fff4e6; border-left-color: #ff9800; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⭐ Rating & Reviews Extractor</h1>
            <p class="subtitle">Extract ratings and reviews from any text - No scraping required!</p>
            
            <div class="info-box">
                ℹ️ Paste any text containing rating and review information. Examples:
                "4.2★ 20596 Ratings, 9777 Reviews" or "Rating: 4.5★ with 10000 ratings"
            </div>
            
            <form id="extractForm" method="POST" action="#" onsubmit="return false;">
                <div class="input-group">
                    <label for="inputText">URLs or Text (one per line for multiple URLs):</label>
                    <textarea 
                        id="inputText" 
                        name="inputText" 
                        placeholder="Paste URLs (one per line) or text containing ratings/reviews here..."
                        required
                    ></textarea>
                    <div class="example">
                        <strong>Example (Multiple URLs):</strong><br>
                        https://meesho.com/product1<br>
                        https://meesho.com/product2<br>
                        https://meesho.com/product3
                    </div>
                </div>
                
                <button type="button" id="submitBtn">Extract Ratings & Reviews</button>
            </form>
            
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>Extracting data...</p>
            </div>
            
            <div id="results" class="results"></div>
        </div>
        
        <script>
            // Clear URL parameters on load
            if (window.location.search) {
                window.history.replaceState({}, document.title, window.location.pathname);
            }
            
            async function handleExtract() {
                const inputText = document.getElementById('inputText').value;
                const submitBtn = document.getElementById('submitBtn');
                const loading = document.getElementById('loading');
                const resultsDiv = document.getElementById('results');
                
                // Split input by lines
                const inputs = inputText.split('\n').filter(line => line.trim());
                const isUrl = (text) => text.trim().match(/^https?:\/\/|^www\./);
                const urls = inputs.filter(line => isUrl(line.trim()));
                
                loading.style.display = 'block';
                resultsDiv.style.display = 'block';
                submitBtn.disabled = true;
                submitBtn.textContent = 'Processing...';
                
                let html = '';
                
                // Show initial status
                resultsDiv.innerHTML = '<div class="result-item"><div class="result-label">Processing ' + inputs.length + ' item(s)...</div></div>';
                
                for (let i = 0; i < inputs.length; i++) {
                    const input = inputs[i].trim();
                    
                    // Show processing status
                    html += 
                        '<div class="url-result">' +
                            '<div class="url-header">URL ' + (i+1) + '/' + inputs.length + ': ' + input.substring(0, 50) + '...</div>' +
                            '<div class="url-content">' +
                                '<div class="result-item processing">' +
                                    '<div class="result-label">⏳ Processing...</div>' +
                                '</div>' +
                            '</div>' +
                        '</div>';
                    resultsDiv.innerHTML = html;
                    
                    try {
                        const response = await fetch('/extract', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ text: input })
                        });
                        
                        const data = await response.json();
                        
                        let resultHtml = '';
                        if (data.success && (data.rating || data.rating_count || data.review_count)) {
                            resultHtml = '<div class="result-item success"><div class="result-label">✅ Success</div></div>';
                            
                            if (data.rating) {
                                resultHtml += '<div class="result-item">' +
                                    '<div class="result-label">Rating</div>' +
                                    '<div class="result-value">' + data.rating + '</div>' +
                                '</div>';
                            }
                            
                            if (data.rating_count) {
                                resultHtml += '<div class="result-item">' +
                                    '<div class="result-label">Ratings Count</div>' +
                                    '<div class="result-value">' + data.rating_count + '</div>' +
                                '</div>';
                            }
                            
                            if (data.review_count) {
                                resultHtml += '<div class="result-item">' +
                                    '<div class="result-label">Reviews Count</div>' +
                                    '<div class="result-value">' + data.review_count + '</div>' +
                                '</div>';
                            }
                        } else {
                            resultHtml = '<div class="result-item error">' +
                                '<div class="result-label">❌ Error</div>' +
                                '<div class="result-value">' + (data.error || 'No ratings/reviews found') + '</div>' +
                            '</div>';
                        }
                        
                        // Update the current URL's result
                        let urlResults = html.match(/\<div class=\"url-result\"\>.*?URL.*?\<\/div\>/g);
                        if (urlResults && urlResults[i]) {
                            html = html.replace(urlResults[i], 
                                '<div class="url-result">' +
                                    '<div class="url-header">URL ' + (i+1) + '/' + inputs.length + ': ' + input.substring(0, 50) + '...</div>' +
                                    '<div class="url-content">' + resultHtml + '</div>' +
                                '</div>');
                        }
                        resultsDiv.innerHTML = html;
                    } catch (error) {
                        let resultHtml = 
                            '<div class="result-item error">' +
                                '<div class="result-label">❌ Error</div>' +
                                '<div class="result-value">' + error.message + '</div>' +
                            '</div>';
                        
                        let urlResults = html.match(/\<div class=\"url-result\"\>.*?URL.*?\<\/div\>/g);
                        if (urlResults && urlResults[i]) {
                            html = html.replace(urlResults[i], 
                                '<div class="url-result">' +
                                    '<div class="url-header">URL ' + (i+1) + '/' + inputs.length + ': ' + input.substring(0, 50) + '...</div>' +
                                    '<div class="url-content">' + resultHtml + '</div>' +
                                '</div>');
                        }
                        resultsDiv.innerHTML = html;
                    }
                }
                
                loading.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Extract Ratings & Reviews';
            }
            
            // Attach click handler to button
            window.addEventListener('DOMContentLoaded', function() {
                const submitBtn = document.getElementById('submitBtn');
                submitBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    handleExtract();
                });
            });
        </script>
    </body>
    </html>
    '''

@app.route('/extract', methods=['POST'])
def extract_ratings():
    """Extract ratings and reviews from text or URL"""
    try:
        data = request.json
        input_text = data.get('text', '').strip()
        
        if not input_text:
            return jsonify({'success': False, 'error': 'Text or URL is required'})
        
        print(f"\n[INFO] Processing: {input_text[:100]}...")
        
        # Check if it's a URL
        is_url = input_text.startswith(('http://', 'https://', 'www.'))
        
        if is_url:
            print(f"[INFO] Detected URL - fetching page...")
            
            # Setup browser
            options = uc.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Normalize URL
            if input_text.startswith('www.'):
                input_text = 'https://' + input_text
            elif not input_text.startswith('http'):
                input_text = 'https://' + input_text
            
            driver = uc.Chrome(options=options)
            
            try:
                print(f"[INFO] Navigating to: {input_text}")
                driver.get(input_text)
                
                # Wait for page to load with multiple attempts
                print(f"[INFO] Waiting for page to load...")
                
                # Wait longer and retry if needed
                max_retries = 3
                for attempt in range(max_retries):
                    time.sleep(8)
                    try:
                        page_text = driver.find_element(By.TAG_NAME, 'body').text
                        if len(page_text) > 100:  # Got some content
                            print(f"[INFO] Page loaded successfully! Length: {len(page_text)} characters")
                            break
                        else:
                            print(f"[INFO] Attempt {attempt+1}: Page text too short ({len(page_text)} chars), retrying...")
                    except:
                        print(f"[INFO] Attempt {attempt+1}: Error getting page content, retrying...")
                else:
                    page_text = driver.find_element(By.TAG_NAME, 'body').text
                
                print(f"[INFO] Final page text length: {len(page_text)} characters")
                
                # Extract using regex patterns
                result = extract_rating_reviews(page_text)
                
                # Debug: if no data found, try to see what's in the page
                if not result['rating'] and not result['rating_count']:
                    print(f"[DEBUG] Sample page text: {page_text[:500]}")
                
            finally:
                try:
                    driver.quit()
                except:
                    pass
        else:
            # Extract from text directly
            print(f"[INFO] Processing as text...")
            result = extract_rating_reviews(input_text)
        
        if result['rating'] or result['rating_count'] or result['review_count']:
            print(f"[SUCCESS] Extracted: {result}")
            return jsonify({
                'success': True,
                'rating': result['rating'],
                'rating_count': result['rating_count'],
                'review_count': result['review_count']
            })
        else:
            print(f"[ERROR] No data found")
            return jsonify({
                'success': False,
                'error': 'No rating or review data found'
            })
            
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] {error_msg}")
        return jsonify({
            'success': False,
            'error': f'Failed to extract: {error_msg}'
        })

if __name__ == '__main__':
    print("="*80)
    print("Rating & Reviews Extractor")
    print("="*80)
    print("Starting Flask server on http://localhost:5003")
    print("Open your browser and go to http://localhost:5003")
    print("="*80)
    app.run(debug=True, host='0.0.0.0', port=5003)

