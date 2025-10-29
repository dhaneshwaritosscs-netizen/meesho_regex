#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid app: URL scraping + AI model for extraction
"""

import sys
import io

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

import os
# Set HuggingFace token from environment variable or use a placeholder
# Users should set HF_TOKEN environment variable or update this file locally
# os.environ['HF_TOKEN'] = 'your_token_here'

from flask import Flask, request, jsonify
import re
import time
import shutil
import subprocess
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# Import AI model (will use if available, otherwise fallback to regex)
try:
    from inference import generate_reviews_json
    AI_MODEL_AVAILABLE = True
    print("[INFO] AI Model enabled")
except ImportError as e:
    print(f"[INFO] AI Model not available: {e}. Using regex fallback.")
    AI_MODEL_AVAILABLE = False

app = Flask(__name__)

def extract_with_ai(text):
    """Extract using AI model"""
    try:
        if not AI_MODEL_AVAILABLE:
            return None
        
        result = generate_reviews_json(text)
        
        if 'json' in result:
            return {
                'rating': result['json'].get('Rating'),
                'rating_count': result['json'].get('Rating_Count'),
                'review_count': result['json'].get('Review_Count'),
                'method': 'AI'
            }
    except Exception as e:
        print(f"[WARNING] AI extraction failed: {e}")
    
    return None

def extract_with_regex(text):
    """Extract using regex patterns (fallback)"""
    result = {
        'rating': None,
        'rating_count': None,
        'review_count': None,
        'method': 'Regex'
    }
    
    # Extract rating
    rating_patterns = [
        r'(\d+\.\d+)\s*\*+',
        r'(\d+\.\d+)\s*★+',
        r'rating[:\s]+(\d+\.\d+)',
        r'(\d+\.\d+)',
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
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hybrid Rating Extractor - URL + AI</title>
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
            .method-badge {
                display: inline-block;
                padding: 3px 8px;
                background: #667eea;
                color: white;
                border-radius: 5px;
                font-size: 11px;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Hybrid Rating Extractor</h1>
            <p class="subtitle">URL Scraping + AI Model for Smart Extraction</p>
            
            <div class="info-box">
                ℹ️ Paste URL to scrape and extract using AI model. Works with Meesho and other sites.
            </div>
            
            <form id="extractForm">
                <div class="input-group">
                    <label for="inputText">Product URL:</label>
                    <textarea 
                        id="inputText" 
                        name="inputText" 
                        placeholder="https://www.meesho.com/product-url..."
                        required
                    ></textarea>
                    <div class="example">
                        <strong>Example:</strong> https://www.meesho.com/glace-cotton-bedsheet-for-double-bed-with-pillow-cover/p/6066q7
                    </div>
                </div>
                
                <button type="submit" id="submitBtn">Extract with AI Model</button>
            </form>
            
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>Scraping and extracting...</p>
            </div>
            
            <div id="results" class="results"></div>
        </div>
        
        <script>
            document.getElementById('extractForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const inputText = document.getElementById('inputText').value;
                const submitBtn = document.getElementById('submitBtn');
                const loading = document.getElementById('loading');
                const resultsDiv = document.getElementById('results');
                
                loading.style.display = 'block';
                resultsDiv.style.display = 'none';
                submitBtn.disabled = true;
                submitBtn.textContent = 'Extracting...';
                
                try {
                    const response = await fetch('/extract', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: inputText })
                    });
                    
                    const data = await response.json();
                    
                    let html = '';
                    if (data.success) {
                        html = `<div class="result-item success">
                            <div class="result-label">✅ Success (${data.method || 'Regex'})</div>
                        </div>`;
                        
                        if (data.rating) {
                            html += `<div class="result-item">
                                <div class="result-label">Rating</div>
                                <div class="result-value">${data.rating}</div>
                            </div>`;
                        }
                        
                        if (data.rating_count) {
                            html += `<div class="result-item">
                                <div class="result-label">Ratings Count</div>
                                <div class="result-value">${data.rating_count}</div>
                            </div>`;
                        }
                        
                        if (data.review_count) {
                            html += `<div class="result-item">
                                <div class="result-label">Reviews Count</div>
                                <div class="result-value">${data.review_count}</div>
                            </div>`;
                        }
                    } else {
                        html = `<div class="result-item error">
                            <div class="result-label">❌ Error</div>
                            <div class="result-value">${data.error || 'Failed to extract'}</div>
                        </div>`;
                    }
                    
                    resultsDiv.innerHTML = html;
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
                    submitBtn.textContent = 'Extract with AI Model';
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/extract', methods=['POST'])
def extract_ratings():
    """Extract from URL using scraping + AI model"""
    try:
        data = request.json
        input_text = data.get('text', '').strip()
        
        if not input_text:
            return jsonify({'success': False, 'error': 'URL is required'})
        
        print(f"\n[INFO] Processing URL: {input_text[:100]}...")
        
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
            print(f"[INFO] Navigating to: {input_text}")
            driver.get(input_text)
            time.sleep(8)
            
            # Get page content
            page_text = driver.find_element(By.TAG_NAME, 'body').text
            print(f"[INFO] Page text length: {len(page_text)} characters")
            
            # Try AI extraction first, fallback to regex
            result = extract_with_ai(page_text)
            
            if not result:
                print("[INFO] AI not available, using regex...")
                result = extract_with_regex(page_text)
            
            if result.get('rating') or result.get('rating_count') or result.get('review_count'):
                print(f"[SUCCESS] Extracted: {result}")
                return jsonify({
                    'success': True,
                    'rating': result.get('rating'),
                    'rating_count': result.get('rating_count'),
                    'review_count': result.get('review_count'),
                    'method': result.get('method', 'Regex')
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No rating data found'
                })
                
        finally:
            try:
                driver.quit()
            except:
                pass
                
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] {error_msg}")
        return jsonify({
            'success': False,
            'error': f'Failed: {error_msg}'
        })

if __name__ == '__main__':
    print("="*80)
    print("Hybrid Rating Extractor - URL Scraping + AI Model")
    print("="*80)
    print("Starting Flask server on http://localhost:5004")
    print("Open your browser and go to http://localhost:5004")
    print("="*80)
    app.run(debug=True, host='0.0.0.0', port=5004)

