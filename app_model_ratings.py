#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Flask app for extracting ratings and reviews using LLM model
NO SCRAPING - Pure model-based extraction
"""

import sys
import io
import os

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

# Set HuggingFace token from environment variable or use a placeholder
# Users should set HF_TOKEN environment variable or update this file locally
# os.environ['HF_TOKEN'] = 'your_token_here'

from flask import Flask, request, jsonify
from inference import generate_reviews_json

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Meesho Rating & Reviews Extractor (LLM Model)</title>
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
            
            .input-group {
                margin-bottom: 25px;
            }
            
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
            
            .info-box {
                background: #f0f4ff;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 5px;
                font-size: 14px;
                color: #555;
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
            
            .example-text {
                font-size: 12px;
                color: #999;
                margin-top: 5px;
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
            <h1>🤖 Meesho Rating Extractor (LLM Model)</h1>
            <p class="subtitle">Extract ratings and reviews using AI model - No web scraping required</p>
            
            <div class="info-box">
                ℹ️ Enter text containing rating and review information. 
                Example: "Rating: 4.2★ Rating Count: 20596 Ratings Review Count: 9777 Reviews"
            </div>
            
            <form id="extractForm">
                <div class="input-group">
                    <label for="inputText">Text with Rating & Review Info:</label>
                    <textarea 
                        id="inputText" 
                        name="inputText" 
                        placeholder="Example: Rating: 4.2★ Rating Count: 20596 Ratings Review Count: 9777 Reviews"
                        required
                    ></textarea>
                    <p class="example-text">📝 Paste any text that contains rating (e.g., 4.2★), ratings count, and reviews count</p>
                </div>
                
                <button type="submit" id="submitBtn">Extract with AI Model</button>
            </form>
            
            <div id="loading" class="loading" style="display: none;">
                <div class="spinner"></div>
                <p>Processing with LLM...</p>
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
                
                // Show loading, hide results
                loading.style.display = 'block';
                resultsDiv.style.display = 'none';
                submitBtn.disabled = true;
                submitBtn.textContent = 'Processing...';
                
                try {
                    const response = await fetch('/extract', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ text: inputText })
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
                    submitBtn.textContent = 'Extract with AI Model';
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/extract', methods=['POST'])
def extract_ratings():
    """Extract ratings and reviews using LLM model"""
    try:
        data = request.json
        input_text = data.get('text', '').strip()
        
        if not input_text:
            return jsonify({'success': False, 'error': 'Text is required'})
        
        print(f"\n[INFO] Extracting from text input...")
        print(f"[DEBUG] Input text: {input_text[:200]}...")
        
        # Use LLM model to extract
        result = generate_reviews_json(input_text)
        
        print(f"[DEBUG] Model result: {result}")
        
        if 'json' in result:
            extracted = result['json']
            
            return jsonify({
                'success': True,
                'rating': extracted.get('Rating'),
                'rating_count': extracted.get('Rating_Count'),
                'review_count': extracted.get('Review_Count'),
                'raw_data': extracted
            })
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"[ERROR] {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
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
    print("Meesho Rating & Reviews Extractor (LLM Model)")
    print("="*80)
    print("Starting Flask server on http://localhost:5002")
    print("Open your browser and go to http://localhost:5002")
    print("="*80)
    app.run(debug=True, host='0.0.0.0', port=5002)

