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
import os
import shutil
import subprocess
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
            
            # Normalize URL
            if input_text.startswith('www.'):
                input_text = 'https://' + input_text
            elif not input_text.startswith('http'):
                input_text = 'https://' + input_text
            
            # Clean up ChromeDriver cache before initialization to avoid file conflicts
            def cleanup_chromedriver_cache():
                """Clean up ChromeDriver cache files that might cause conflicts"""
                try:
                    cache_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "undetected_chromedriver")
                    if os.path.exists(cache_dir):
                        print(f"[INFO] Cleaning up ChromeDriver cache...")
                        # Remove the entire cache directory to force fresh download
                        try:
                            shutil.rmtree(cache_dir)
                            print(f"[INFO] Removed ChromeDriver cache directory")
                        except Exception as e:
                            print(f"[WARNING] Could not remove cache directory: {e}")
                            # Try to remove specific problematic files
                            target_file = os.path.join(cache_dir, "undetected_chromedriver.exe")
                            if os.path.exists(target_file):
                                try:
                                    os.remove(target_file)
                                    print(f"[INFO] Removed problematic file: {target_file}")
                                except:
                                    pass
                            # Try to remove files in nested directories
                            for root, dirs, files in os.walk(cache_dir):
                                for file in files:
                                    if 'chromedriver' in file.lower():
                                        try:
                                            file_path = os.path.join(root, file)
                                            os.remove(file_path)
                                        except:
                                            pass
                except Exception as cleanup_error:
                    print(f"[WARNING] Cleanup failed: {cleanup_error}")
            
            # Get Chrome version for compatibility
            def get_chrome_version():
                """Try to detect Chrome version"""
                try:
                    # Try to get Chrome version from registry (Windows)
                    result = subprocess.run(
                        ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'version' in line.lower():
                                version_str = line.split()[-1]
                                # Extract major version number (e.g., 141 from 141.0.7390.123)
                                major_version = int(version_str.split('.')[0])
                                print(f"[INFO] Detected Chrome version: {version_str} (major: {major_version})")
                                return major_version
                except Exception as e:
                    print(f"[INFO] Could not detect Chrome version: {e}")
                return None
            
            # Clean up cache before first attempt
            cleanup_chromedriver_cache()
            
            # Setup browser with proper error handling
            driver = None
            max_attempts = 3
            chrome_version = get_chrome_version()
            
            for attempt in range(max_attempts):
                try:
                    options = uc.ChromeOptions()
                    options.add_argument("--start-maximized")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--disable-blink-features=AutomationControlled")
                    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                    
                    # Use detected Chrome version if available, otherwise let uc auto-detect
                    driver_kwargs = {
                        'options': options,
                        'use_subprocess': True,
                        'driver_executable_path': None
                    }
                    
                    # Specify version_main if we detected it, otherwise let uc handle it
                    if chrome_version:
                        driver_kwargs['version_main'] = chrome_version
                        print(f"[INFO] Using ChromeDriver version {chrome_version} to match Chrome browser")
                    else:
                        driver_kwargs['version_main'] = None  # Auto-detect
                        print(f"[INFO] Auto-detecting ChromeDriver version")
                    
                    driver = uc.Chrome(**driver_kwargs)
                    print(f"[INFO] ChromeDriver initialized successfully")
                    break
                    
                except Exception as driver_error:
                    error_str = str(driver_error)
                    print(f"[WARNING] Attempt {attempt + 1}/{max_attempts}: {error_str}")
                    
                    # Handle file conflict error (WinError 183) - clean up and retry
                    if "WinError 183" in error_str or "Cannot create a file when that file already exists" in error_str:
                        print(f"[INFO] File conflict detected, cleaning up cache...")
                        cleanup_chromedriver_cache()
                        time.sleep(1)
                    
                    # Handle version mismatch - force cleanup and retry
                    if "version" in error_str.lower() or "ChromeDriver only supports" in error_str or "session not created" in error_str.lower():
                        print(f"[INFO] Version mismatch detected, cleaning up cache for fresh download...")
                        cleanup_chromedriver_cache()
                        time.sleep(1)
                    
                    if attempt < max_attempts - 1:
                        time.sleep(2)  # Wait before retry
                    else:
                        # Last attempt failed, raise the error
                        raise Exception(f"Failed to initialize ChromeDriver after {max_attempts} attempts: {error_str}")
            
            if driver is None:
                raise Exception("Failed to initialize ChromeDriver")
            
            try:
                # Set page load timeout
                driver.set_page_load_timeout(60)  # 60 seconds max for page load
                
                print(f"[INFO] Navigating to: {input_text}")
                try:
                    driver.get(input_text)
                    # Initial wait for potential redirects/JavaScript checks
                    print(f"[INFO] Initial wait for page redirects/checks...")
                    time.sleep(5)
                except Exception as nav_error:
                    # Page load timeout - try to get what we can
                    nav_error_str = str(nav_error)
                    if "timeout" in nav_error_str.lower() or "page load" in nav_error_str.lower():
                        print(f"[WARNING] Page load timeout, trying to get content anyway...")
                        # Continue - might still have content
                    else:
                        raise
                
                # Wait for page to load with multiple attempts and explicit waits
                print(f"[INFO] Checking page content and waiting for proper load...")
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                # Function to check if page is blocked/access denied
                def is_access_denied(page_source, page_text):
                    """Check if page shows access denied or blocking message"""
                    if not page_source and not page_text:
                        return True
                    
                    blocked_keywords = [
                        'access denied', 'blocked', 'cloudflare', 
                        'checking your browser', 'please wait', 
                        'verify you are human', 'challenge',
                        'temporarily unavailable', 'bot detected',
                        'rate limited', '403 forbidden', 'forbidden',
                        'unauthorized access', 'permission denied'
                    ]
                    
                    combined_text = (page_source or '').lower() + ' ' + (page_text or '').lower()
                    
                    # Check for keywords
                    for keyword in blocked_keywords:
                        if keyword in combined_text:
                            return True
                    
                    # Also check if page is too short and contains common blocking indicators
                    if len(combined_text) < 200:
                        if any(indicator in combined_text for indicator in ['cloudflare', 'checking', 'wait']):
                            return True
                    
                    return False
                
                page_text = None
                page_source = None
                max_retries = 8  # Increased retries for access denied scenarios
                access_denied_retries = 3  # Specific retries for access denied
                
                for attempt in range(max_retries):
                    try:
                        # Wait for body element with explicit wait
                        wait = WebDriverWait(driver, 10)
                        body_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                        
                        # Get page content
                        page_text = driver.find_element(By.TAG_NAME, 'body').text
                        page_source = driver.page_source
                        
                        # Check if we're on an access denied page
                        if is_access_denied(page_source, page_text):
                            print(f"[WARNING] Attempt {attempt+1}: Access denied/blocked page detected")
                            
                            # If this is early in attempts, wait and refresh
                            if attempt < access_denied_retries:
                                print(f"[INFO] Waiting for page to redirect/reload (attempt {attempt+1}/{access_denied_retries})...")
                                time.sleep(8)  # Wait longer for redirect
                                
                                # Try refreshing the page
                                print(f"[INFO] Attempting to refresh page...")
                                try:
                                    driver.refresh()
                                    time.sleep(5)  # Wait after refresh
                                    
                                    # Check again after refresh
                                    page_text = driver.find_element(By.TAG_NAME, 'body').text
                                    page_source = driver.page_source
                                    
                                    if not is_access_denied(page_source, page_text):
                                        print(f"[INFO] Page loaded successfully after refresh!")
                                        break
                                    else:
                                        print(f"[INFO] Still blocked after refresh, will retry...")
                                except Exception as refresh_error:
                                    print(f"[WARNING] Refresh failed: {refresh_error}")
                            else:
                                print(f"[INFO] Access denied persisted after {access_denied_retries} attempts")
                            continue
                        
                        # Check if we have sufficient content
                        if len(page_text) > 100:  # Got some content
                            print(f"[INFO] Page loaded successfully! Length: {len(page_text)} characters")
                            break
                        else:
                            print(f"[INFO] Attempt {attempt+1}: Page text too short ({len(page_text)} chars), waiting more...")
                            time.sleep(5)  # Wait longer for dynamic content
                            
                    except Exception as wait_error:
                        error_str = str(wait_error)
                        print(f"[INFO] Attempt {attempt+1}: {error_str}")
                        if attempt < max_retries - 1:
                            # If error, try refreshing once
                            if attempt == max_retries // 2:  # Try refresh at midpoint
                                try:
                                    print(f"[INFO] Attempting page refresh due to error...")
                                    driver.refresh()
                                    time.sleep(5)
                                except:
                                    pass
                            time.sleep(5)
                        else:
                            # Last attempt - try to get whatever we can
                            try:
                                page_text = driver.find_element(By.TAG_NAME, 'body').text
                                page_source = driver.page_source
                            except Exception as e:
                                try:
                                    page_source = driver.page_source  # Fallback to page source
                                    page_text = ""  # Will use page_source for extraction
                                except:
                                    raise Exception(f"Could not retrieve page content: {str(wait_error)}")
                
                # Final check if we still have access denied
                if page_source:
                    final_page_text = page_text or ""
                    if is_access_denied(page_source, final_page_text):
                        print(f"[WARNING] Final page still shows access denied, but attempting extraction anyway...")
                        # Continue anyway - might have some useful data
                
                if not page_text or len(page_text) < 50:
                    # Try using page_source if page_text is insufficient
                    if page_source and len(page_source) > 500:
                        print(f"[INFO] Using page source for extraction (text too short)")
                        # Extract text from HTML as fallback
                        from bs4 import BeautifulSoup
                        try:
                            soup = BeautifulSoup(page_source, 'html.parser')
                            page_text = soup.get_text()
                        except:
                            page_text = page_source
                    
                    if (not page_text or len(page_text) < 50) and (not page_source or len(page_source) < 500):
                        raise Exception("Could not load page content - page may be blocking automation or taking too long to load")
                
                print(f"[INFO] Final page text length: {len(page_text)} characters")
                
                # Extract using regex patterns
                result = extract_rating_reviews(page_text)
                
                # Debug: if no data found, try to see what's in the page
                if not result['rating'] and not result['rating_count']:
                    print(f"[DEBUG] Sample page text: {page_text[:500]}")
                
            finally:
                try:
                    if driver:
                        driver.quit()
                except Exception as quit_error:
                    print(f"[WARNING] Error closing driver: {quit_error}")
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
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Traceback: {error_trace}")
        
        # Provide more user-friendly error messages
        if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            user_error = "Request timed out - the website took too long to respond. Please try again."
        elif "could not load page content" in error_msg.lower() or "blocking automation" in error_msg.lower():
            user_error = "Could not access page - the website may be blocking automated access or the page structure changed."
        elif "Failed to initialize ChromeDriver" in error_msg:
            user_error = "Browser initialization failed. Please restart the application."
        else:
            user_error = f"Failed to extract: {error_msg[:200]}"  # Limit error message length
        
        return jsonify({
            'success': False,
            'error': user_error
        })

if __name__ == '__main__':
    print("="*80)
    print("Rating & Reviews Extractor")
    print("="*80)
    print("Starting Flask server on http://localhost:5003")
    print("Open your browser and go to http://localhost:5003")
    print("="*80)
    app.run(debug=True, host='0.0.0.0', port=5003)

