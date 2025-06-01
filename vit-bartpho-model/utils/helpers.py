import wandb
import os
from dotenv import load_dotenv

def setup_wandb_auth(use_wandb=True):
    """Authenticate with Weights & Biases using multiple authentication methods."""
    if not use_wandb:
        print("Weights & Biases logging is disabled.")
        return False
    
    # Method 1: Try to load from .env file
    try:
        load_dotenv()
        wandb_api_key = os.getenv("WANDB_API_KEY")
        if wandb_api_key:
            wandb.login(key=wandb_api_key)
            print("Successfully authenticated with Weights & Biases using .env file")
            return True
    except Exception as e:
        print(f"Error loading API key from .env file: {str(e)}")
    
    # Method 2: Try to load from environment variables
    try:
        wandb_api_key = os.environ.get("WANDB_API_KEY")
        if wandb_api_key:
            wandb.login(key=wandb_api_key)
            print("Successfully authenticated with Weights & Biases using environment variable")
            return True
    except Exception as e:
        print(f"Error loading API key from environment variable: {str(e)}")
    
    # Method 3: Try to load from config file
    try:
        config_path = os.path.join(os.path.expanduser("~"), ".wandb_config")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                wandb_api_key = f.read().strip()
            if wandb_api_key:
                wandb.login(key=wandb_api_key)
                print("Successfully authenticated with Weights & Biases using config file")
                return True
    except Exception as e:
        print(f"Error loading API key from config file: {str(e)}")
    

def load_saved_model(artifact_path, model_class, feature_extractor_class, device="cuda", use_wandb=True):
    """Load a saved model from an artifact path or local directory."""
    if not use_wandb:
        # If wandb is disabled, assume artifact_path is a local directory
        try:
            feature_extractor = feature_extractor_class.from_pretrained(artifact_path)
            model = model_class.from_pretrained(artifact_path)
            model = model.to(device)
            
            print(f"Successfully loaded model from local path: {artifact_path}")
            return model, feature_extractor
        except Exception as e:
            print(f"Error loading model from local path {artifact_path}: {str(e)}")
            return None, None
    else:
        # Use wandb to load model
        try:
            run = wandb.init(project="ViT-BARTpho", job_type="inference")
            artifact = run.use_artifact(artifact_path, type='model')
            artifact_dir = artifact.download()
            
            feature_extractor = feature_extractor_class.from_pretrained(artifact_dir)
            model = model_class.from_pretrained(artifact_dir)
            model = model.to(device)
            
            print(f"Successfully loaded model from wandb artifact: {artifact_path}")
            return model, feature_extractor
        except Exception as e:
            print(f"Error loading model from wandb artifact {artifact_path}: {str(e)}")
            return None, None
