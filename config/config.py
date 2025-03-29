class Config:
    # Data paths
    TRAIN_DATA_PATH = '/kaggle/input/ktvic-bartpho/data/train_data.json'
    TEST_DATA_PATH = '/kaggle/input/ktvic-bartpho/data/test_data.json'
    TRAIN_IMAGES_DIR = '/kaggle/input/ktvic-bartpho/data/train-images'
    TEST_IMAGES_DIR = '/kaggle/input/ktvic-bartpho/data/public-test-images'
    DATASET_SAVE_PATH = './dataset/image_caption_dataset'
    
    GROUNDTRUTH_FILE = '/kaggle/working/vietnamese-image-captioning/data/grouped_captions.json'
    
    # Model parameters
    IMAGE_ENCODER_MODEL = "google/vit-large-patch16-224-in21k"
    TEXT_DECODER_MODEL = "vinai/bartpho-word"
    MAX_TARGET_LENGTH = 64
    
    # Training parameters
    BATCH_SIZE = 8
    EVAL_BATCH_SIZE = 8
    WEIGHT_DECAY = 1e-6
    FP16 = True
    
    # Inference parameters
    NUM_BEAMS = 3
    DO_SAMPLE = False
    MAX_LENGTH = 24
    
    # Paths
    OUTPUT_DIR = "./output"
    LOGS_DIR = "./logs"
    RESULT_FILE = "./result.json"
    
    # Wandb configuration
    USE_WANDB = True  # Flag to control whether to use wandb or not
    WANDB_PROJECT = "ViT-BARTpho_batch8"
    WANDB_RUN_NAME = "experiment"
    WANDB_SAVE_CHECKPOINT = True
