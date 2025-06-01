import torch
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from app.config.settings import MODEL_PATH
from app.utils.db import get_db_connection
import os
import logging

# Global variables for model components
model = None
feature_extractor = None
tokenizer = None

def load_model():
    """
    Tải model image captioning từ đường dẫn được chỉ định
    """
    global model, feature_extractor, tokenizer, MODEL_PATH
    
    # Try to get active model from database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT model_path FROM model_versions WHERE is_active = TRUE LIMIT 1")
        active_model = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if active_model:
            MODEL_PATH = active_model[0]
            logging.info(f"Loading active model from database: {MODEL_PATH}")
    except Exception as e:
        logging.error(f"Error getting active model from database: {str(e)}")
        logging.info(f"Using default model path: {MODEL_PATH}")
    
    # Check if model path exists
    if not os.path.exists(MODEL_PATH):
        logging.error(f"Model path does not exist: {MODEL_PATH}")
        logging.info("Checking alternative paths...")
        
        # Try alternative paths
        alt_paths = [
            "/app/artifacts",
            os.path.join(os.path.dirname(__file__), '..', '..', 'artifacts'),
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'artifacts'))
        ]
        
        for path in alt_paths:
            if os.path.exists(path):
                logging.info(f"Found alternative model path: {path}")
                MODEL_PATH = path
                break
        else:
            logging.error("No valid model path found. Model loading will likely fail.")
    
    # Only load if not already loaded or force reload
    if model is None:
        try:
            logging.info(f"Starting model loading from {MODEL_PATH}")
            
            # List files in model directory for debugging
            if os.path.exists(MODEL_PATH):
                logging.info(f"Contents of model directory: {os.listdir(MODEL_PATH)}")
            
            # Load the model components
            model = VisionEncoderDecoderModel.from_pretrained(MODEL_PATH)
            feature_extractor = ViTImageProcessor.from_pretrained(MODEL_PATH)
            
            # Load tokenizer - update the path if needed
            tokenizer_path = "vinai/bartpho-word"
            logging.info(f"Loading tokenizer from {tokenizer_path}")
            tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
            
            # Set the device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = model.to(device)
            
            # Set model configuration
            model.config.decoder_start_token_id = tokenizer.bos_token_id
            model.config.pad_token_id = tokenizer.pad_token_id
            
            logging.info(f"Model loaded successfully on {device}")
        except Exception as e:
            logging.error(f"Error loading model: {str(e)}")
            import traceback
            traceback.print_exc()
            # If there's an error loading the model, set the model variables to None
            model = None
            feature_extractor = None

def format_caption(caption):
    """
    Format the caption: remove underscores, capitalize first letter, add period
    """
    # Remove underscores
    formatted = caption.replace('_', ' ')
    
    # Capitalize the first letter
    if formatted:
        formatted = formatted[0].upper() + formatted[1:]
    
    # Add period at the end if not present
    if formatted and not formatted.endswith(('.', '!', '?')):
        formatted += '.'
                                              
    return formatted

def generate_caption(image):
    """
    Tạo caption cho một hình ảnh sử dụng model đã tải
    """
    global model, feature_extractor, tokenizer
    
    # Kiểm tra xem model đã được tải chưa
    if model is None or feature_extractor is None or tokenizer is None:
        logging.info("Model components not loaded, attempting to load now")
        load_model()
        
        # Nếu vẫn không tải được model
        if model is None:
            logging.error("Failed to load model components, cannot generate caption")
            return None
    
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Processing image for caption generation on {device}")
        pixel_values = feature_extractor(image, return_tensors="pt").pixel_values.to(device)
        
        with torch.no_grad():
            logging.info("Generating caption...")
            generated_ids = model.generate(
                pixel_values, 
                num_beams=3, 
                do_sample=False, 
                max_length=24
            )
        
        # Decode caption
        raw_caption = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        formatted_caption = format_caption(raw_caption)
        logging.info(f"Caption generated: '{formatted_caption}'")
        
        return formatted_caption
    except Exception as e:
        logging.error(f"Error generating caption: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


'''


docker build -t asia-east1-docker.pkg.dev/vietnamese-image-captioning/docker-repo/flask-backend:latest .

docker push asia-east1-docker.pkg.dev/vietnamese-image-captioning/docker-repo/flask-backend:latest
asia-east1-docker.pkg.dev/vietnamese-image-captioning/docker-repo

gcloud artifacts repositories describe docker-repo \
    --project=vietnamese-image-captioning \
    --location=asia-east1

docker push asia-east1-docker.pkg.dev/vietnamese-image-captioning/docker-repo/flask-backend:latest


docker login -u ya29.c.c0ASRK0GbnFCyBy1JDB1jbIBuX_NBSr5wcwPChZJutq40b5AhCT2r8pSJQgbYE2HbXehDxws9PWeItSdawYvL0fsQ-6Oa3l9MQaromgpuqNeKPfWCoAs7TYCsu9GKbp4xx2TXFnvFBosAMDgAy6S00JyPayKuokjHUid1JqqHu4ukix3P_YEP4donIDHD2dpxXsUf_vYVXSNwpOQ1_cwqgCosZhIIMCOFfDsrwY0ssvoga6jtjhR8bsA44-J85QY7BUm-dH-kD8WhtNtbfXrpdIW5e31K9fFIoxTsJz8Xdt6Lh5Bu10erP2KSJ_vZz9ceTzT08siNMARZXUvEYVY9iVXC7Ms2psYbb_A7u4-aICYm_QfIPkIjUliGt9C7m5LHO1IBc0AG399AvX2ofJ2R555M8swhnkBomaaog1iqof5YjYq3wJW-BXcwd285xOYna_Wl9ZhIznRbFd6cy6r1-vo51WqOVieJQFfjr0Yp9sBdOWFa1lqdz31InIv6kyfBxB-3wvJwVXnf5fwhc3u17VeO-Yt8mws9ymSrfWb5zWt_g3Xi8SBaan-9FrWZui0W_zb83g8Yk3r_19ohfyb45epF85Fgb-Zil9-2rZqM0UI9xaS17XpUz-qvwuekbQ4QcFRFvh24udjRqffit-rx2B3RJXt-Z0oBbmh5SkzmBU1vs09QS0ukypi8xe6St0UU9cZm5-zq3YkdO7R9tV8IwZJI5cmQiMXop6lSkXjM8aXj_mYUzYR4ldY26m1oh8kFswOd17lzhhy79J0F7uMMWFfW9V2kefwj8kcqSs1sOq-JjXIZ_4d1Za87S8lnkwu9WbXSbbB-o6eluQl27Zmje9ut-hB4u7nIi0o2v9V469xIvdZXt4hpuvStSIpqQq3tzeQRxz3j6q34Oxg1IR3xac4Qj4YBqs2Ma24BaVzRpQ9Mi0JkwQQOFSi7ay9ySMfqw9egZhsjg1ahtJhVg0jyoV8M5uqYgvQ6uq54BaxabUYXcltzgFxI_ibR --password-stdin https://asia-east1-docker.pkg.dev

gcloud auth configure-docker asia-east1-docker.pkg.dev


gcloud run deploy flask-backend \ 
    --image=asia-east1-docker.pkg.dev/vietnamese-image-captioning/docker-repo/flask-backend:latest \
    --platform=managed \
    --region=asia-east1 \ 
    --allow-unauthenticated \ 
    --port=5000 \
    --memory=16Gi \
    --cpu=8 \
    --add-cloudsql-instances vietnamese-image-captioning:asia-east1:vietnamese-image-caption-db \
    --set-env-vars "DB_HOST=/cloudsql/vietnamese-image-captioning:asia-east1:vietnamese-image-caption-db" \
    --set-env-vars "DB_USER=postgres" \
    --set-env-vars "DB_PASS=postgres" \
    --set-env-vars "DB_NAME=image_caption_db"\
    --set-env-vars "DB_PORT=5432"

    

    gcloud run deploy flask-backend \
  --image=asia-east1-docker.pkg.dev/vietnamese-image-captioning/docker-repo/flask-backend:latest \
  --platform=managed \
  --region=asia-east1 \
  --allow-unauthenticated \
  --port=5000 \
  --memory=16Gi \
  --cpu=8 \
  --add-cloudsql-instances vietnamese-image-captioning:asia-east1:vietnamese-image-caption-db \
  --set-env-vars "DB_HOST=/cloudsql/vietnamese-image-captioning:asia-east1:vietnamese-image-caption-db" \
  --set-env-vars "DB_USER=postgres" \
  --set-env-vars "DB_PASS=postgres" \
  --set-env-vars "DB_NAME=image_caption_db" \
  --set-env-vars "DB_PORT=5432"

'''