import wandb
import os
from kaggle_secrets import UserSecretsClient

def setup_wandb_auth(use_wandb=True):
    """Authenticate with Weights & Biases using Kaggle secrets."""
    if not use_wandb:
        print("Weights & Biases logging is disabled.")
        return False
    
    try:
        user_secrets = UserSecretsClient()
        wandb_api_key = user_secrets.get_secret("wandb_api_key")
        wandb.login(key=wandb_api_key)
        print("Successfully authenticated with Weights & Biases")
        return True
    except Exception as e:
        print(f"Error authenticating with Weights & Biases: {str(e)}")
        print("Continuing without Weights & Biases logging")
        return False

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
