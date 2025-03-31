"""Configuration parameters for the ViT-BARTpho Image Captioning model."""

# Model configuration
IMAGE_ENCODER_MODEL = "google/vit-large-patch16-224-in21k"
TEXT_DECODER_MODEL = "vinai/bartpho-word"

# # Data paths
# TRAIN_DATA_PATH = '/run/media/trong/New Volume/Algo/KTVIC/processed_ktvic/train_data.json'
# TEST_DATA_PATH = '/run/media/trong/New Volume/Algo/KTVIC/processed_ktvic/test_data.json'
# TRAIN_IMAGES_DIR = '/run/media/trong/New Volume/Algo/KTVIC/processed_ktvic/train-images'
# TEST_IMAGES_DIR = '/run/media/trong/New Volume/Algo/KTVIC/processed_ktvic/public-test-images'
# GROUNDTRUTH_FILE = '/run/media/trong/New Volume/Algo/ViT-BARTpho/data/groundtruth_captions.json'

# Data paths
TRAIN_DATA_PATH = '/kaggle/input/ktvic-bartpho/data/train_data.json'
TEST_DATA_PATH = '/kaggle/input/ktvic-bartpho/data/test_data.json'
TRAIN_IMAGES_DIR = '/kaggle/input/ktvic-bartpho/data/train-images'
TEST_IMAGES_DIR = '/kaggle/input/ktvic-bartpho/data/public-test-images'

GROUNDTRUTH_FILE = '/kaggle/working/vit-bartpho/data/groundtruth_captions.json'

# Training parameters
MAX_TARGET_LENGTH = 64
SEED = 42
BATCH_SIZE = 8
EVAL_BATCH_SIZE = 8
WEIGHT_DECAY = 1e-6
USE_FP16 = True

# Quick testing/subset parameters
USE_SUBSET = False  # Set to True for quick testing with subset of data
TRAIN_SUBSET_SIZE = 5  # Number of samples to use from training set
TEST_SUBSET_SIZE = 5    # Number of samples to use from test set

# Inference parameters
MAX_LENGTH = 24
NUM_BEAMS = 3

# Paths
DATASET_SAVE_PATH = './dataset/image_caption_dataset'
OUTPUT_DIR = './output'
LOGS_DIR = './logs'
WANDB_PROJECT = "ViT-BARTpho_3-30"
WANDB_NAME = "experiment"

# Device
DEVICE = 'cuda'  # 'cuda' or 'cpu'
