# inference.py
import json, re
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
import torch
import os

MODEL = "meta-llama/Llama-2-7b-chat-hf"   # LLaMA-2 Model
ADAPTER = "output-llama-lora-comprehensive"  # comprehensive attributes adapter
ADAPTER_REVIEWS = "output-llama-lora-reviews-ratings"  # reviews and ratings adapter

# Global variables for model loading
tokenizer = None
model = None
model_loaded = False

# Global variables for reviews/ratings model
reviews_tokenizer = None
reviews_model = None
reviews_model_loaded = False

def load_model():
    """Load the model and tokenizer only once"""
    global tokenizer, model, model_loaded
    
    if not model_loaded:
        try:
            print("Loading tokenizer and model...")
            tokenizer = AutoTokenizer.from_pretrained(MODEL, use_fast=False)
            tokenizer.pad_token = tokenizer.eos_token

            # Check if adapter exists
            if not os.path.exists(ADAPTER):
                print(f"WARNING: Adapter {ADAPTER} not found. Using base model only.")
                model = AutoModelForCausalLM.from_pretrained(
                    MODEL, 
                    device_map="auto", 
                    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    trust_remote_code=True
                )
            else:
                # Load base model and wrap with PEFT adapter
                base = AutoModelForCausalLM.from_pretrained(
                    MODEL, 
                    device_map="auto", 
                    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    trust_remote_code=True
                )
                model = PeftModel.from_pretrained(base, ADAPTER)
            
            model_loaded = True
            print("Model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            model_loaded = False
            raise e

def load_reviews_model():
    """Load the reviews and ratings model and tokenizer"""
    global reviews_tokenizer, reviews_model, reviews_model_loaded
    
    if not reviews_model_loaded:
        try:
            print("Loading reviews/ratings tokenizer and model...")
            reviews_tokenizer = AutoTokenizer.from_pretrained(MODEL, use_fast=False)
            reviews_tokenizer.pad_token = reviews_tokenizer.eos_token

            # Check if reviews adapter exists
            if not os.path.exists(ADAPTER_REVIEWS):
                print(f"WARNING: Reviews adapter {ADAPTER_REVIEWS} not found. Using base model only.")
                reviews_model = AutoModelForCausalLM.from_pretrained(
                    MODEL, 
                    device_map="auto", 
                    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    trust_remote_code=True
                )
            else:
                # Load base model and wrap with PEFT adapter
                base = AutoModelForCausalLM.from_pretrained(
                    MODEL, 
                    device_map="auto", 
                    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    trust_remote_code=True
                )
                reviews_model = PeftModel.from_pretrained(base, ADAPTER_REVIEWS)
            
            reviews_model_loaded = True
            print("Reviews/Ratings model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading reviews model: {e}")
            reviews_model_loaded = False
            raise e

def build_prompt(text):
    instr = "Extract product attributes as JSON with keys exactly: Brand_Name, Models, Colors, Sizes/Ounce, Designs, Pattern, Costumes, Team_Names, Styles, Sets, Flavors, Pack, Albums, Movies, Formats, Edition, Platform, Digital_Copy, Refurbished, Remanufactured, Pre-Owned. Focus especially on extracting detailed design features, visual elements, materials, and construction details for the Designs field. Respond ONLY with a JSON object. Use null for missing fields."
    prompt = f"### Instruction:\n{instr}\n\n### Input:\n{text}\n\n### Output:\n"
    return prompt

def build_reviews_prompt(text):
    instr = "Extract product reviews and ratings as JSON with keys exactly: Rating, Rating_Count, Review_Count. Respond ONLY with a JSON object. Use null for missing fields."
    prompt = f"### Instruction:\n{instr}\n\n### Input:\n{text}\n\n### Output:\n"
    return prompt

def generate_json(text, max_new_tokens=256, temperature=0.0):
    """Generate JSON extraction from product text"""
    try:
        load_model()
        
        prompt = build_prompt(text)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            generation_output = model.generate(
                **inputs, 
                max_new_tokens=max_new_tokens, 
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
        
        decoded = tokenizer.decode(generation_output[0], skip_special_tokens=True)
        
        # Extract JSON from response
        m = re.search(r'(\{.*\})', decoded, re.S)
        if not m:
            # fallback: try from last newline
            try:
                candidate = decoded.split("### Output:")[-1].strip()
                m = re.search(r'(\{.*\})', candidate, re.S)
            except Exception:
                m = None
        
        if not m:
            return {"error": "no json found", "raw": decoded}
        
        json_str = m.group(1)
        try:
            parsed = json.loads(json_str)
            return {"json": parsed}
        except json.JSONDecodeError as e:
            return {"error": "json parse error", "raw": json_str, "decoded": decoded, "exception": str(e)}
    
    except Exception as e:
        return {"error": f"Model inference error: {str(e)}"}

def generate_reviews_json(text, max_new_tokens=128, temperature=0.0):
    """Generate JSON extraction for reviews and ratings"""
    try:
        load_reviews_model()
        
        prompt = build_reviews_prompt(text)
        inputs = reviews_tokenizer(prompt, return_tensors="pt").to(reviews_model.device)
        
        with torch.no_grad():
            generation_output = reviews_model.generate(
                **inputs, 
                max_new_tokens=max_new_tokens, 
                do_sample=False,
                pad_token_id=reviews_tokenizer.eos_token_id
            )
        
        decoded = reviews_tokenizer.decode(generation_output[0], skip_special_tokens=True)
        
        # Extract JSON from response
        m = re.search(r'(\{.*\})', decoded, re.S)
        if not m:
            # fallback: try from last newline
            try:
                candidate = decoded.split("### Output:")[-1].strip()
                m = re.search(r'(\{.*\})', candidate, re.S)
            except Exception:
                m = None
        
        if not m:
            return {"error": "no json found", "raw": decoded}
        
        json_str = m.group(1)
        try:
            parsed = json.loads(json_str)
            return {"json": parsed}
        except json.JSONDecodeError as e:
            return {"error": "json parse error", "raw": json_str, "decoded": decoded, "exception": str(e)}
    
    except Exception as e:
        return {"error": f"Reviews model inference error: {str(e)}"}

def extract_reviews_ratings(product_data):
    """Extract reviews and ratings using the trained model"""
    try:
        # Extract rating and rating count from product data
        rating = product_data.get('rating', '')
        rating_count = product_data.get('rating_count', '')
        
        # If rating info is already in product_data, use it
        if rating or rating_count:
            input_text = ""
            if rating:
                input_text += f"Rating: \"{rating}\" "
            if rating_count:
                input_text += f"Rating Count: \"{rating_count}\""
            
            # Use model to extract structured format
            result = generate_reviews_json(input_text)
            
            if 'json' in result:
                extracted = result['json']
                
                # Store extracted ratings and reviews
                if extracted.get('Rating'):
                    product_data['rating'] = extracted['Rating']
                if extracted.get('Rating_Count'):
                    product_data['rating_count'] = extracted['Rating_Count']
                if extracted.get('Review_Count'):
                    product_data['review_count'] = extracted['Review_Count']
                
                # Store all extracted reviews data
                product_data['reviews_data'] = extracted
            
            return product_data
        
        return product_data
    
    except Exception as e:
        print(f"Error in reviews/ratings extraction: {str(e)}")
        return product_data

def extract_with_model(product_data):
    """Extract attributes using the trained model with enhanced design focus"""
    try:
        # Build input text from product data with enhanced design context
        text_parts = []
        
        if product_data.get('name'):
            text_parts.append(f"Title: \"{product_data['name']}\"")
        
        if product_data.get('brand'):
            text_parts.append(f"Brand: \"{product_data['brand']}\"")
        
        if product_data.get('price'):
            text_parts.append(f"Price: \"{product_data['price']}\"")
        
        if product_data.get('description'):
            text_parts.append(f"Description: \"{product_data['description']}\"")
        
        if product_data.get('sku'):
            text_parts.append(f"SKU: \"{product_data['sku']}\"")
        
        # Add size information
        if product_data.get('size_chart'):
            sizes = [s.get('size', '') for s in product_data['size_chart'] if s.get('size')]
            if sizes:
                text_parts.append(f"Sizes: \"{', '.join(sizes)}\"")
        
        # Add color information if available
        if product_data.get('colors'):
            text_parts.append(f"Colors: \"{product_data['colors']}\"")
        
        # Add materials and specifications for design context
        if product_data.get('materials'):
            text_parts.append(f"Materials: \"{', '.join(product_data['materials'])}\"")
        
        if product_data.get('specifications'):
            text_parts.append(f"Specifications: \"{', '.join(product_data['specifications'])}\"")
        
        # Add any existing design information
        if product_data.get('designs'):
            text_parts.append(f"Design Features: \"{product_data['designs']}\"")
        
        input_text = " ".join(text_parts)
        
        if not input_text.strip():
            return product_data
        
        # Use model to extract attributes
        result = generate_json(input_text)
        
        if 'json' in result:
            extracted = result['json']
            
            # Map extracted attributes back to product data
            if extracted.get('Brand_Name') and not product_data.get('brand'):
                product_data['brand'] = extracted['Brand_Name']
            
            if extracted.get('Models') and not product_data.get('model'):
                product_data['model'] = extracted['Models']
            
            if extracted.get('Colors') and not product_data.get('colors'):
                product_data['colors'] = extracted['Colors']
            
            if extracted.get('Sizes/Ounce') and not product_data.get('extracted_sizes'):
                product_data['extracted_sizes'] = extracted['Sizes/Ounce']
            
            # Enhanced design extraction
            if extracted.get('Designs'):
                designs = extracted['Designs']
                if designs and designs != 'null':
                    # Split designs into individual features if it's a string
                    if isinstance(designs, str):
                        design_features = [d.strip() for d in designs.split(',') if d.strip()]
                        product_data['design_features'] = design_features
                        product_data['designs'] = designs
                    else:
                        product_data['designs'] = designs
            
            # Extract all other attributes
            if extracted.get('Pattern'):
                product_data['pattern'] = extracted['Pattern']
            
            if extracted.get('Costumes'):
                product_data['costumes'] = extracted['Costumes']
            
            if extracted.get('Team_Names'):
                product_data['team_names'] = extracted['Team_Names']
            
            if extracted.get('Styles'):
                product_data['styles'] = extracted['Styles']
            
            if extracted.get('Sets'):
                product_data['sets'] = extracted['Sets']
            
            if extracted.get('Flavors'):
                product_data['flavors'] = extracted['Flavors']
            
            if extracted.get('Pack'):
                product_data['pack'] = extracted['Pack']
            
            if extracted.get('Albums'):
                product_data['albums'] = extracted['Albums']
            
            if extracted.get('Movies'):
                product_data['movies'] = extracted['Movies']
            
            if extracted.get('Formats'):
                product_data['formats'] = extracted['Formats']
            
            if extracted.get('Edition'):
                product_data['edition'] = extracted['Edition']
            
            if extracted.get('Platform'):
                product_data['platform'] = extracted['Platform']
            
            if extracted.get('Digital_Copy'):
                product_data['digital_copy'] = extracted['Digital_Copy']
            
            if extracted.get('Refurbished'):
                product_data['refurbished'] = extracted['Refurbished']
            
            if extracted.get('Remanufactured'):
                product_data['remanufactured'] = extracted['Remanufactured']
            
            if extracted.get('Pre-Owned'):
                product_data['pre_owned'] = extracted['Pre-Owned']
            
            # Store all extracted attributes
            product_data['ai_extracted'] = extracted
        
        # Also extract reviews and ratings if available
        product_data = extract_reviews_ratings(product_data)
        
        return product_data
    
    except Exception as e:
        print(f"Error in model extraction: {str(e)}")
        return product_data

if __name__ == "__main__":
    # Example
    text = "Title: \"Acme UltraSneak 3000 - Men's Running Shoes - Blue/White - Size 10\" Description: \"Lightweight, breathable mesh, EVA sole. Price: $89.99\""
    out = generate_json(text)
    print(json.dumps(out, indent=2, ensure_ascii=False))