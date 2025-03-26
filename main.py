import argparse
import torch
import os
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer

from config.config import Config
from data.data_loader import prepare_dataset
from data.dataset import ImageCaptioningDataset
from models.encoder_decoder import load_model_and_processors
from training.trainer import setup_training, train_model
from inference.captioning import generate_caption, display_captioned_image, run_inference_on_test_set
from utils.helpers import setup_wandb_auth

def parse_args():
    parser = argparse.ArgumentParser(description="Vietnamese Image Captioning")
    parser.add_argument('--mode', type=str, choices=['train', 'inference', 'demo'], default='train',
                        help='Mode: train, inference, or demo')
    parser.add_argument('--model_path', type=str, default=None,
                        help='Path to pre-trained model for inference or demo')
    parser.add_argument('--image_path', type=str, default=None,
                        help='Path to image for demo mode')
    parser.add_argument('--use_wandb', action='store_true', default=None,
                        help='Use Weights & Biases for logging')
    return parser.parse_args()

def train():
    """Run the training pipeline."""
    print("Starting training pipeline...")
    
    # Set up wandb authentication if enabled
    use_wandb = setup_wandb_auth(Config.USE_WANDB)
    
    # Update Config.USE_WANDB based on the result of authentication
    Config.USE_WANDB = use_wandb
    
    # Prepare dataset
    print("Preparing dataset...")
    dataset = prepare_dataset(
        Config.TRAIN_DATA_PATH, 
        Config.TEST_DATA_PATH, 
        Config.TRAIN_IMAGES_DIR, 
        Config.TEST_IMAGES_DIR, 
        Config.DATASET_SAVE_PATH
    )
    
    # Load model and processors
    print("Loading model and processors...")
    model, feature_extractor, tokenizer = load_model_and_processors(
        Config.IMAGE_ENCODER_MODEL, Config.TEXT_DECODER_MODEL
    )
    
    # Create datasets
    print("Creating training and evaluation datasets...")
    train_dataset = ImageCaptioningDataset(
        dataset, 'train', Config.MAX_TARGET_LENGTH, tokenizer, feature_extractor
    )
    eval_dataset = ImageCaptioningDataset(
        dataset, 'test', Config.MAX_TARGET_LENGTH, tokenizer, feature_extractor
    )
    
    # Setup training
    print("Setting up trainer...")
    trainer = setup_training(model,feature_extractor, tokenizer, train_dataset, eval_dataset, Config)
    
    # Train model
    print("Starting training...")
    trained_model = train_model(trainer)
    
    print("Training completed successfully!")
    return trained_model, feature_extractor, tokenizer

def inference(model_path=None):
    """Run inference on test dataset."""
    print("Starting inference pipeline...")
    
    # Set up wandb authentication if enabled
    use_wandb = setup_wandb_auth(Config.USE_WANDB)
    
    # Update Config.USE_WANDB based on the result of authentication
    Config.USE_WANDB = use_wandb
    
    # Load model and processors
    if model_path:
        print(f"Loading model from {model_path}...")
        if Config.USE_WANDB:
            import wandb
            run = wandb.init(project=Config.WANDB_PROJECT)
            artifact = run.use_artifact(model_path, type='model')
            artifact_dir = artifact.download()
        else:
            artifact_dir = model_path  # Assume it's a local path
        
        feature_extractor = ViTImageProcessor.from_pretrained(artifact_dir)
        model = VisionEncoderDecoderModel.from_pretrained(artifact_dir)
        tokenizer = AutoTokenizer.from_pretrained(Config.TEXT_DECODER_MODEL)
    else:
        print("No model path provided. Loading default models...")
        model, feature_extractor, tokenizer = load_model_and_processors(
            Config.IMAGE_ENCODER_MODEL, Config.TEXT_DECODER_MODEL
        )
    
    # Move model to device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    
    # Run inference
    print("Running inference on test dataset...")
    results = run_inference_on_test_set(model, feature_extractor, tokenizer, Config.DATASET_SAVE_PATH, Config)
    
    print(f"Inference completed successfully! Results saved to {Config.RESULT_FILE}")
    return results

def demo(model_path, image_path):
    """Run demo on a single image."""
    if not image_path:
        raise ValueError("Image path is required for demo mode.")
    
    print(f"Running demo on image: {image_path}")
    
    # Set up wandb authentication if enabled
    use_wandb = setup_wandb_auth(Config.USE_WANDB)
    
    # Update Config.USE_WANDB based on the result of authentication
    Config.USE_WANDB = use_wandb
    
    # Load model and processors
    if model_path:
        print(f"Loading model from {model_path}...")
        if Config.USE_WANDB:
            import wandb
            run = wandb.init(project=Config.WANDB_PROJECT)
            artifact = run.use_artifact(model_path, type='model')
            artifact_dir = artifact.download()
        else:
            artifact_dir = model_path  # Assume it's a local path
        
        feature_extractor = ViTImageProcessor.from_pretrained(artifact_dir)
        model = VisionEncoderDecoderModel.from_pretrained(artifact_dir)
        tokenizer = AutoTokenizer.from_pretrained(Config.TEXT_DECODER_MODEL)
    else:
        print("No model path provided. Loading default models...")
        model, feature_extractor, tokenizer = load_model_and_processors(
            Config.IMAGE_ENCODER_MODEL, Config.TEXT_DECODER_MODEL
        )
    
    # Move model to device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    
    # Generate caption
    caption = generate_caption(model, feature_extractor, tokenizer, image_path, device, Config)
    
    # Display image with caption
    display_captioned_image(image_path, caption)
    
    return caption

if __name__ == "__main__":
    args = parse_args()
    
    # Override Config.USE_WANDB if specified in command line
    if args.use_wandb is not None:
        Config.USE_WANDB = args.use_wandb
    
    if args.mode == 'train':
        train()
    elif args.mode == 'inference':
        inference(args.model_path)
    elif args.mode == 'demo':
        demo(args.model_path, args.image_path)
