"""Model configuration and initialization."""

import torch
from transformers import VisionEncoderDecoderModel, AutoTokenizer, ViTImageProcessor

import sys
sys.path.append('..')
from config import IMAGE_ENCODER_MODEL, TEXT_DECODER_MODEL, DEVICE

def load_model_and_processors():
    """Load and configure the model, tokenizer, and feature extractor."""
    # Initialize model
    model = VisionEncoderDecoderModel.from_encoder_decoder_pretrained(
        IMAGE_ENCODER_MODEL, TEXT_DECODER_MODEL)
    
    # Initialize image feature extractor
    feature_extractor = ViTImageProcessor.from_pretrained(IMAGE_ENCODER_MODEL)
    
    # Initialize text tokenizer
    tokenizer = AutoTokenizer.from_pretrained(TEXT_DECODER_MODEL)
    
    # Configure special tokens
    model.config.decoder_start_token_id = tokenizer.bos_token_id
    model.config.pad_token_id = tokenizer.pad_token_id
    
    # Print token configuration for verification
    print("EOS token ID:", tokenizer.eos_token_id)
    print("BOS token ID:", tokenizer.bos_token_id)
    print("PAD token ID:", tokenizer.pad_token_id)
    
    # Move model to device
    model = model.to(DEVICE)
    
    return model, feature_extractor, tokenizer

def load_model_from_checkpoint(checkpoint_path):
    """Load model from a checkpoint."""
    # Initialize components from checkpoint
    feature_extractor = ViTImageProcessor.from_pretrained(checkpoint_path)
    model = VisionEncoderDecoderModel.from_pretrained(checkpoint_path)
    tokenizer = AutoTokenizer.from_pretrained(TEXT_DECODER_MODEL)
    
    # Move model to device
    model = model.to(DEVICE)
    
    return model, feature_extractor, tokenizer
