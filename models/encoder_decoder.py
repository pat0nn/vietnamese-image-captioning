from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer

def load_model_and_processors(image_encoder_model, text_decoder_model):
    """Load the encoder-decoder model, image processor, and tokenizer."""
    # Load the encoder-decoder model
    model = VisionEncoderDecoderModel.from_encoder_decoder_pretrained(
        image_encoder_model, text_decoder_model)
    
    # Load image feature extractor
    feature_extractor = ViTImageProcessor.from_pretrained(image_encoder_model)
    
    # Load text tokenizer
    tokenizer = AutoTokenizer.from_pretrained(text_decoder_model)
    
    # Configure special tokens
    model.config.decoder_start_token_id = tokenizer.bos_token_id
    model.config.pad_token_id = tokenizer.pad_token_id
    
    # Print token info for debugging
    print("EOS token ID:", tokenizer.eos_token_id)
    print("BOS token ID:", tokenizer.bos_token_id)
    print("PAD token ID:", tokenizer.pad_token_id)
    
    return model, feature_extractor, tokenizer
