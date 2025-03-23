import torch
import json
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm
from datasets import load_from_disk

def process_image(image_path, feature_extractor, device):
    """Process an image for inference."""
    image = Image.open(image_path).convert('RGB')
    pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values.to(device)
    return pixel_values, image

def generate_caption(model, feature_extractor, tokenizer, image_path, device, config):
    """Generate a caption for an image."""
    # Process the image
    pixel_values, _ = process_image(image_path, feature_extractor, device)

    # Generate caption
    generated_ids = model.generate(
        pixel_values, 
        num_beams=config.NUM_BEAMS, 
        do_sample=config.DO_SAMPLE, 
        max_length=config.MAX_LENGTH
    )
    
    # Decode the generated ids to text
    generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text

def display_captioned_image(image_path, caption):
    """Display an image with its generated caption."""
    image = Image.open(image_path).convert('RGB')
    plt.figure(figsize=(10, 8))
    plt.imshow(image)
    plt.axis('off')
    plt.title(caption)
    plt.show()
    print("Generated Caption:", caption)

def run_inference_on_test_set(model, feature_extractor, tokenizer, dataset_path, config):
    """Run inference on the entire test dataset."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    
    # Load dataset
    dataset = load_from_disk(dataset_path)
    test_dataset = dataset['test']
    
    # Run inference on all test images
    results = []
    
    for item in tqdm(test_dataset, desc="Generating captions"):
        image_id = item['image_id']
        image_path = item['image_path']
        
        try:
            caption = generate_caption(model, feature_extractor, tokenizer, image_path, device, config)
            results.append({
                "image_id": image_id,
                "caption": caption
            })
        except Exception as e:
            print(f"Error processing image_id {image_id}: {str(e)}")
    
    # Sort results by image_id for consistency
    results.sort(key=lambda x: x["image_id"])
    
    # Save results
    with open(config.RESULT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=None)
    
    print(f"Results saved to {config.RESULT_FILE}")
    return results
