"""Inference utilities for image captioning."""

import json
import torch
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm

import sys
sys.path.append('..')
from config import NUM_BEAMS, MAX_LENGTH, DEVICE

def process_image(image_path, feature_extractor, device=DEVICE):
    """
    Process an image for inference.
    
    Args:
        image_path: Path to the image file
        feature_extractor: Feature extractor for processing the image
        device: Device to use for processing
        
    Returns:
        pixel_values: Processed image tensor
    """
    image = Image.open(image_path).convert('RGB')
    pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values.to(device)
    return pixel_values

def generate_caption(model, feature_extractor, tokenizer, image_path, num_beams=NUM_BEAMS, max_length=MAX_LENGTH):
    """
    Generate a caption for a single image.
    
    Args:
        model: The image captioning model
        feature_extractor: Feature extractor for processing the image
        tokenizer: Tokenizer for decoding predictions
        image_path: Path to the image file
        num_beams: Number of beams for beam search
        max_length: Maximum length of generated caption
        
    Returns:
        generated_text: The generated caption
    """
    pixel_values = process_image(image_path, feature_extractor)
    
    # Set model to evaluation mode
    model.eval()
    
    # Generate caption
    with torch.no_grad():
        generated_ids = model.generate(
            pixel_values, 
            num_beams=num_beams, 
            do_sample=False, 
            max_length=max_length
        )
    
    # Decode the generated IDs to text
    generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return generated_text

def display_image_with_caption(image_path, caption=None):
    """
    Display an image with its caption.
    
    Args:
        image_path: Path to the image file
        caption: Caption to display (optional)
    """
    image = Image.open(image_path).convert('RGB')
    plt.figure(figsize=(10, 8))
    plt.imshow(image)
    plt.axis('off')  # Hide the axes
    
    if caption:
        plt.title(caption, fontsize=12)
    
    plt.tight_layout()
    plt.show()
    
    if caption:
        print("Generated Caption:", caption)

def batch_generate_captions(model, feature_extractor, tokenizer, dataset, num_beams=NUM_BEAMS, max_length=MAX_LENGTH):
    """
    Generate captions for all images in a dataset.
    
    Args:
        model: The image captioning model
        feature_extractor: Feature extractor for processing images
        tokenizer: Tokenizer for decoding predictions
        dataset: Dataset containing images to process
        num_beams: Number of beams for beam search
        max_length: Maximum length of generated captions
        
    Returns:
        results: List of dictionaries with image_id and caption
    """
    model.eval()
    results = []
    
    for item in tqdm(dataset, desc=f"Generating captions (num_beams={num_beams})"):
        image_id = item['image_id']
        image_path = item['image_path']
        
        try:
            caption = generate_caption(
                model, 
                feature_extractor, 
                tokenizer, 
                image_path, 
                num_beams=num_beams, 
                max_length=max_length
            )
            
            results.append({
                "image_id": image_id,
                "caption": caption
            })
        except Exception as e:
            print(f"Error processing image_id {image_id}: {str(e)}")
    
    # Sort results for consistency
    results.sort(key=lambda x: x["image_id"])
    
    return results

def save_results_to_json(results, output_path):
    """
    Save results to a JSON file.
    
    Args:
        results: List of dictionaries with results
        output_path: Path to save the JSON file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=None)
    
    print(f"Results saved to {output_path}")
