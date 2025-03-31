"""
ViT-BARTpho Image Captioning
Main entry point for training and inference.
"""

import argparse
import os
import sys
import torch
import wandb
from pathlib import Path

try:
    # For Kaggle environment
    from kaggle_secrets import UserSecretsClient
    IN_KAGGLE = True
except ImportError:
    IN_KAGGLE = False

from data.data_processor import prepare_dataset, load_from_disk
from models.model_config import load_model_and_processors, load_model_from_checkpoint
from training.trainer import initialize_wandb, setup_training, train_model
from inference.predict import generate_caption, display_image_with_caption, batch_generate_captions, save_results_to_json
from config import DATASET_SAVE_PATH, WANDB_PROJECT, WANDB_NAME, NUM_BEAMS, MAX_LENGTH

def setup_wandb():
    """
    Set up Weights & Biases using environment variable for the API key.
    
    Returns:
        bool: True if W&B was successfully initialized, False otherwise
    """
    try:
        wandb_api_key = os.environ.get("WANDB_API_KEY")
        
        if wandb_api_key:
            print("Found WANDB_API_KEY in environment variables.")
            initialize_wandb(WANDB_PROJECT, WANDB_NAME, wandb_api_key)
            return True
        else:
            print("WANDB_API_KEY not found in environment variables. Skipping W&B initialization.")
            return False
    except Exception as e:
        print(f"Error initializing W&B: {str(e)}")
        print("Continuing without W&B logging.")
        return False

def train(args):
    """Train the model."""
    print("Preparing dataset...")
    if os.path.exists(args.dataset_path) and not args.force_preprocess:
        dataset = load_from_disk(args.dataset_path)
        print(f"Loaded existing dataset from {args.dataset_path}")
    else:
        dataset = prepare_dataset()
    
    # Set up W&B logging if requested
    use_wandb = False
    if args.use_wandb:
        use_wandb = setup_wandb()
    
    print("Loading model and processors...")
    model, feature_extractor, tokenizer = load_model_and_processors()
    
    print("Setting up training...")
    trainer = setup_training(model, feature_extractor, tokenizer, dataset, use_wandb=use_wandb)
    
    print("Starting training...")
    training_output = train_model(trainer)
    
    print("Training completed!")
    return training_output

def inference(args):
    """Run inference on a single image."""
    if args.checkpoint_path:
        print(f"Loading model from checkpoint: {args.checkpoint_path}")
        model, feature_extractor, tokenizer = load_model_from_checkpoint(args.checkpoint_path)
    else:
        print("Loading default model...")
        model, feature_extractor, tokenizer = load_model_and_processors()
    
    if args.image_path:
        print(f"Generating caption for image: {args.image_path}")
        caption = generate_caption(
            model, 
            feature_extractor, 
            tokenizer, 
            args.image_path, 
            num_beams=args.num_beams,
            max_length=args.max_length
        )
        
        display_image_with_caption(args.image_path, caption)
    else:
        print("No image path provided for inference.")

def batch_inference(args):
    """Run inference on the test dataset."""
    print("Loading dataset...")
    if os.path.exists(args.dataset_path):
        dataset = load_from_disk(args.dataset_path)
    else:
        print(f"Dataset not found at {args.dataset_path}. Preparing new dataset...")
        dataset = prepare_dataset()
    
    test_dataset = dataset['test']
    
    if args.checkpoint_path:
        print(f"Loading model from checkpoint: {args.checkpoint_path}")
        model, feature_extractor, tokenizer = load_model_from_checkpoint(args.checkpoint_path)
    else:
        print("Loading default model...")
        model, feature_extractor, tokenizer = load_model_and_processors()
    
    # Define beam range
    if args.beam_range:
        beam_range = range(args.min_beams, args.max_beams + 1)
        print(f"Will run inference with beam sizes from {args.min_beams} to {args.max_beams}")
    else:
        beam_range = [args.num_beams]
        print(f"Will run inference with beam size {args.num_beams}")
    
    for num_beams in beam_range:
        print(f"Running inference with num_beams={num_beams}...")
        
        results = batch_generate_captions(
            model, 
            feature_extractor, 
            tokenizer, 
            test_dataset, 
            num_beams=num_beams,
            max_length=args.max_length
        )
        
        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Create output filename with experiment name
        output_path = os.path.join(
            args.output_dir, 
            f"result_{args.experiment_name}_numBeam{num_beams}.json"
        )
        
        save_results_to_json(results, output_path)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ViT-BARTpho Image Captioning")
    
    # Mode selection
    parser.add_argument(
        "--mode", 
        type=str, 
        default="train", 
        choices=["train", "inference", "batch_inference"],
        help="Operating mode: train, inference, or batch_inference"
    )
    
    # General parameters
    parser.add_argument(
        "--dataset_path", 
        type=str, 
        default=DATASET_SAVE_PATH,
        help="Path to the dataset"
    )
    parser.add_argument(
        "--checkpoint_path", 
        type=str, 
        help="Path to a model checkpoint"
    )
    parser.add_argument(
        "--output_dir", 
        type=str, 
        default="./outputs",
        help="Directory to save outputs"
    )
    parser.add_argument(
        "--use_wandb", 
        action="store_true",
        help="Use Weights & Biases for logging"
    )
    parser.add_argument(
        "--experiment_name", 
        type=str, 
        default="experiment",
        help="Name for the experiment"
    )
    
    # Training parameters
    parser.add_argument(
        "--force_preprocess", 
        action="store_true",
        help="Force preprocessing of data even if dataset exists"
    )
    
    # Inference parameters
    parser.add_argument(
        "--image_path", 
        type=str,
        help="Path to an image for caption generation"
    )
    parser.add_argument(
        "--num_beams", 
        type=int, 
        default=NUM_BEAMS,
        help="Number of beams for beam search"
    )
    parser.add_argument(
        "--max_length", 
        type=int, 
        default=MAX_LENGTH,
        help="Maximum length of generated caption"
    )
    
    # Batch inference parameters
    parser.add_argument(
        "--beam_range", 
        action="store_true",
        help="Use a range of beam sizes for batch inference"
    )
    parser.add_argument(
        "--min_beams", 
        type=int, 
        default=1,
        help="Minimum number of beams (for beam range)"
    )
    parser.add_argument(
        "--max_beams", 
        type=int, 
        default=7,
        help="Maximum number of beams (for beam range)"
    )
    
    return parser.parse_args()

def main():
    """Main entry point."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Create output directory if needed
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
    
    # Execute the appropriate mode
    if args.mode == "train":
        train(args)
    elif args.mode == "inference":
        if not args.image_path:
            print("Error: --image_path is required for inference mode")
            sys.exit(1)
        inference(args)
    elif args.mode == "batch_inference":
        batch_inference(args)
    else:
        print(f"Unknown mode: {args.mode}")
        sys.exit(1)
    
    print(f"{args.mode} completed successfully!")

if __name__ == "__main__":
    main()
