"""Data processing utilities for loading and processing image captioning data."""

import json
import os
import random
import pandas as pd
from datasets import Dataset, DatasetDict, load_from_disk
import sys

sys.path.append('..')
from config import TRAIN_DATA_PATH, TEST_DATA_PATH, TRAIN_IMAGES_DIR, TEST_IMAGES_DIR, DATASET_SAVE_PATH, SEED

def load_data(json_path):
    """Load data from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def process_train_val_data(data, images_dir=TRAIN_IMAGES_DIR):
    """Process the train data to create the desired structure."""
    # Extract images data
    images = {}
    for img in data['images']:
        # Extract filename without extension for image_id
        if 'id' in img:
            image_id = img['id']
        else:
            # If id is not present, extract from filename
            image_id = int(os.path.splitext(img['filename'])[0])
        
        images[image_id] = {
            'file_name': img['filename'],
            'image_id': image_id,
        }
    
    # Process annotations
    records = []
    for i, ann in enumerate(data['annotations']):
        if 'image_id' in ann:
            image_id = ann['image_id']
        else:
            # For the given example, annotations might not have image_id
            # We'll assume annotations are grouped by image (5 per image)
            image_id = data['images'][i // 5]['id'] if 'id' in data['images'][i // 5] else int(os.path.splitext(data['images'][i // 5]['filename'])[0])
        
        if image_id in images:
            # Use segment_caption instead of caption
            caption = ann.get('segment_caption', '')
            
            record = {
                'image_id': image_id,
                'caption_id': i,
                'caption': caption,
                'file_name': images[image_id]['file_name'],
                'image_path': os.path.join(images_dir, images[image_id]['file_name'])
            }
            records.append(record)
    
    return records

def process_test_data(data, images_dir=TEST_IMAGES_DIR):
    """Process the test data to create the desired structure, selecting only the first caption for each image."""
    records = []
    
    # Create a mapping of image_id to segment_caption
    image_captions = {}
    for annotation in data['annotations']:
        image_id = annotation['image_id']
        if image_id not in image_captions:
            image_captions[image_id] = annotation.get('segment_caption', '')
    
    # Process images
    for img in data['images']:
        filename = img['filename']
        image_id = int(os.path.splitext(filename)[0])
        caption = image_captions.get(image_id, '')
        
        record = {
            'image_id': image_id,
            'caption_id': image_id,  
            'caption': caption,
            'file_name': filename,
            'image_path': os.path.join(images_dir, filename)
        }
        records.append(record)
    
    return records

def prepare_train_data(records, seed=SEED):
    """Prepare the train records."""
    # Shuffle the records with a fixed random seed for reproducibility
    random.seed(seed)
    random.shuffle(records)
    
    # Verify no consecutive identical images in groups of 5
    train_records = verify_and_fix_consecutive_images(records)
    
    print(f"Total train records: {len(train_records)}")
    
    return train_records

def verify_and_fix_consecutive_images(records, max_consecutive=5):
    """
    Verify that there are no more than max_consecutive identical images in a row.
    If found, reshuffles the records until the condition is met.
    """
    verified = False
    attempt_count = 0
    max_attempts = 10  # Limit the number of shuffle attempts
    
    while not verified and attempt_count < max_attempts:
        verified = True
        for i in range(0, len(records) - max_consecutive + 1):
            # Check if the next max_consecutive records have the same image_id
            if len(set(record['image_id'] for record in records[i:i+max_consecutive])) == 1:
                verified = False
                random.shuffle(records)  # Reshuffle and try again
                attempt_count += 1
                break
    
    if not verified:
        # If we couldn't fix with simple shuffling, use a more aggressive approach
        print(f"Warning: Could not eliminate consecutive images after {max_attempts} shuffles.")
        print("Using more aggressive shuffling method...")
        records = aggressive_shuffle(records, max_consecutive)
        
    return records

def aggressive_shuffle(records, max_consecutive):
    """
    A more aggressive approach to avoid consecutive identical images.
    Groups records by image_id, then interleaves them.
    """
    # Group records by image_id
    grouped_records = {}
    for record in records:
        img_id = record['image_id']
        if img_id not in grouped_records:
            grouped_records[img_id] = []
        grouped_records[img_id].append(record)
    
    # Shuffle each group
    for img_id in grouped_records:
        random.shuffle(grouped_records[img_id])
    
    # Interleave records from different groups
    shuffled_records = []
    groups = list(grouped_records.values())
    random.shuffle(groups)  # Shuffle the order of groups
    
    # Take one record from each group in a round-robin fashion
    while any(len(group) > 0 for group in groups):
        for group in groups:
            if group:
                shuffled_records.append(group.pop(0))
    
    return shuffled_records

def create_huggingface_dataset(train_records, test_records):
    """Create a HuggingFace dataset from processed records."""
    train_df = pd.DataFrame(train_records)
    test_df = pd.DataFrame(test_records)
    
    train_dataset = Dataset.from_pandas(train_df)
    test_dataset = Dataset.from_pandas(test_df)
    
    # Create DatasetDict with train and test splits
    dataset_dict = DatasetDict({
        'train': train_dataset,
        'test': test_dataset
    })
    
    return dataset_dict

def find_consecutive_images(records, max_consecutive=5):
    """Find groups of consecutive records with the same image_id"""
    consecutive_groups = []
    for i in range(0, len(records) - max_consecutive + 1):
        image_ids = [record['image_id'] for record in records[i:i+max_consecutive]]
        if len(set(image_ids)) == 1:
            consecutive_groups.append(i)
    return consecutive_groups

def prepare_dataset():
    """Prepare and save the dataset."""
    # Load train data
    train_data = load_data(TRAIN_DATA_PATH)
    
    # Process train data
    train_records = process_train_val_data(train_data)
    
    # Prepare train data (no validation split)
    train_records = prepare_train_data(train_records)
    
    # Load and process test data
    test_data = load_data(TEST_DATA_PATH)
    test_records = process_test_data(test_data)
    print(f"Test records: {len(test_records)}")
    
    # Create HuggingFace dataset
    dataset = create_huggingface_dataset(train_records, test_records)
    
    # Print dataset info
    print(dataset)
    
    # Verify no consecutive identical images in final dataset
    print("Verifying train split...")
    consecutive_groups = find_consecutive_images(train_records)
    if consecutive_groups:
        print(f"Warning: Found {len(consecutive_groups)} groups of consecutive identical images in train split")
    else:
        print("Train split verification passed: No consecutive identical images found")
    
    # Save dataset
    dataset.save_to_disk(DATASET_SAVE_PATH)
    
    print(f"Dataset has been saved to {DATASET_SAVE_PATH}")
    
    return dataset

if __name__ == "__main__":
    prepare_dataset()
