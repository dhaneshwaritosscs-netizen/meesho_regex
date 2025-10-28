# Reviews and Ratings Extraction with LLM

This module extracts product reviews and ratings information using a fine-tuned Llama-2 model.

## Features

- **Rating Extraction**: Extracts numerical rating (e.g., "4.2★")
- **Rating Count**: Extracts total number of ratings (e.g., "20596 Ratings")
- **Review Count**: Extracts total number of reviews (e.g., "9777 Reviews")

## Overview

Based on the Meesho product page example, the system extracts:
- **Rating**: "4.2★" (shown in green box with star icon)
- **Rating Count**: "20596 Ratings"
- **Review Count**: "9777 Reviews"

## Training Data

The training data is located in:
- `data/reviews_ratings_train.jsonl` - Training samples
- `data/reviews_ratings_val.jsonl` - Validation samples

### Training Data Format

Each line contains:
```json
{
  "instruction": "Extract product reviews and ratings as JSON with keys exactly: Rating, Rating_Count, Review_Count...",
  "input": "Rating: \"4.2★\" Rating Count: \"20596 Ratings\" Review Count: \"9777 Reviews\"",
  "output": "{\"Rating\": \"4.2★\", \"Rating_Count\": \"20596 Ratings\", \"Review_Count\": \"9777 Reviews\"}"
}
```

## Training the Model

To train the model for reviews and ratings extraction:

```bash
python train_reviews_ratings.py
```

### Training Configuration

- **Model**: meta-llama/Llama-2-7b-chat-hf
- **Output Directory**: `output-llama-lora-reviews-ratings`
- **Training File**: `data/reviews_ratings_train.jsonl`
- **Validation File**: `data/reviews_ratings_val.jsonl`
- **Epochs**: 30
- **Learning Rate**: 2e-5
- **Batch Size**: 1
- **LoRA Rank**: 32

## Using the Model

### Basic Usage

```python
from inference import extract_reviews_ratings, generate_reviews_json

# Option 1: Direct JSON generation
result = generate_reviews_json("Rating: \"4.2★\" Rating Count: \"20596 Ratings\"")

# Option 2: Extract from product data
product_data = {
    'name': 'Casual Polyester Blend Coffee Top',
    'price': '₹197',
    'rating': '4.2★',
    'rating_count': '20596 Ratings, 9777 Reviews'
}

result = extract_reviews_ratings(product_data)
print(result)
```

### Expected Output

```json
{
  "rating": "4.2★",
  "rating_count": "20596 Ratings",
  "review_count": "9777 Reviews",
  "reviews_data": {
    "Rating": "4.2★",
    "Rating_Count": "20596 Ratings",
    "Review_Count": "9777 Reviews"
  }
}
```

## Integration with Main App

The reviews and ratings extraction is automatically integrated with the main extraction pipeline in `inference.py`:

```python
from inference import extract_with_model

# Product data from crawler or web scraping
product_data = {
    'name': 'Product Name',
    'price': '₹197',
    'rating': '4.2★',
    'rating_count': '20596 Ratings'
}

# Extract comprehensive attributes + reviews/ratings
result = extract_with_model(product_data)
```

## Testing

Run the test script to verify the reviews and ratings extraction:

```bash
python test_reviews_ratings.py
```

This will test:
1. Direct JSON generation from rating information
2. Integration with product data extraction
3. Validation of extracted fields

## Integration with Crawler

The Meesho crawler script (user-provided) already extracts rating and rating_count. The LLM model then standardizes this data:

**From Crawler:**
```python
{
    'rating': '4.2★',
    'rating_count': '20596 Ratings, 9777 Reviews'
}
```

**After LLM Processing:**
```python
{
    'rating': '4.2★',
    'rating_count': '20596 Ratings',
    'review_count': '9777 Reviews',
    'reviews_data': {
        'Rating': '4.2★',
        'Rating_Count': '20596 Ratings',
        'Review_Count': '9777 Reviews'
    }
}
```

## Data Fields

### Input Fields (from Crawler)

- `rating` (string): Star rating with star symbol (e.g., "4.2★")
- `rating_count` (string): Combined rating and review count (e.g., "20596 Ratings, 9777 Reviews")

### Output Fields (from LLM)

- `Rating` (string): Standardized rating format (e.g., "4.2★")
- `Rating_Count` (string): Total number of ratings (e.g., "20596 Ratings")
- `Review_Count` (string): Total number of reviews (e.g., "9777 Reviews")

## File Structure

```
├── data/
│   ├── reviews_ratings_train.jsonl    # Training data
│   └── reviews_ratings_val.jsonl       # Validation data
├── inference.py                         # Main inference code
├── train_reviews_ratings.py             # Training script
├── test_reviews_ratings.py              # Test script
└── REVIEWS_RATINGS_README.md           # This file
```

## Model Architecture

- **Base Model**: Llama-2-7b-chat-hf
- **Fine-tuning Method**: LoRA (Low-Rank Adaptation)
- **LoRA Config**:
  - r: 32
  - alpha: 64
  - dropout: 0.05
  - Target modules: q_proj, k_proj, v_proj, o_proj

## Requirements

Make sure you have installed:

```bash
pip install transformers peft torch datasets accelerate
```

## Notes

1. The model is trained to extract 3 specific fields: Rating, Rating_Count, Review_Count
2. The input format must match the training data format for best results
3. The model handles missing fields gracefully by returning `null`
4. The system works alongside the comprehensive attributes model

## Examples

### Example 1: High-rated Product

```python
input = "Rating: \"4.8★\" Rating Count: \"12450 Ratings\" Review Count: \"8650 Reviews\""
output = {
    "Rating": "4.8★",
    "Rating_Count": "12450 Ratings",
    "Review_Count": "8650 Reviews"
}
```

### Example 2: Low-rated Product

```python
input = "Rating: \"3.5★\" Rating Count: \"8500 Ratings\" Review Count: \"5200 Reviews\""
output = {
    "Rating": "3.5★",
    "Rating_Count": "8500 Ratings",
    "Review_Count": "5200 Reviews"
}
```

### Example 3: Missing Data

```python
input = "Rating: \"4.2★\""
output = {
    "Rating": "4.2★",
    "Rating_Count": null,
    "Review_Count": null
}
```

## Troubleshooting

### Model Not Found Error

If you get an error that the adapter is not found:
```bash
python train_reviews_ratings.py
```

### CUDA Out of Memory

Reduce the batch size or use CPU:
```python
# In train_reviews_ratings.py
BATCH_SIZE = 1  # Reduce if needed
```

### Poor Extraction Results

1. Add more training data to `data/reviews_ratings_train.jsonl`
2. Increase training epochs in `train_reviews_ratings.py`
3. Adjust learning rate and other hyperparameters

