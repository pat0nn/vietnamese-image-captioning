# ViT-BARTpho Image Captioning

A modular implementation of image captioning using Vision Transformer (ViT) as encoder and BARTpho as decoder for Vietnamese captions.

## Project Description

This project combines the Vision Transformer (ViT) model for image encoding with the BARTpho model for Vietnamese text generation to create an end-to-end image captioning system specifically designed for Vietnamese. The system takes an image as input and generates a descriptive caption in Vietnamese, leveraging the powerful visual understanding capabilities of ViT and the natural language generation abilities of BARTpho.

Key features:
- Pre-trained ViT for robust image feature extraction
- BARTpho for high-quality Vietnamese text generation
- Support for Weights & Biases (wandb) experiment tracking
- Comprehensive evaluation metrics (BLEU, ROUGE, etc.)
- Support for batch inference with different beam search sizes

## Project Structure

```
ViT-BARTpho-project/
├── data/
│   └── data_processor.py    # Data loading and processing utilities
├── models/
│   └── model_config.py      # Model configuration and setup
├── training/
│   ├── dataset.py           # Custom dataset implementation
│   ├── metrics.py           # Evaluation metrics
│   └── trainer.py           # Training utilities
├── inference/
│   └── predict.py           # Inference utilities
├── utils/
│   └── callbacks.py         # Custom callbacks
├── config.py                # Configuration parameters
└── main.py                  # Main entry point
```

## Prerequisites

- Python 3.11
- Transformers 4.18+
- Datasets 2.0+
- Weights & Biases (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/pat0nn/vietnamese-image-captioning.git
cd vit-bartpho-model
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up Weights & Biases for experiment tracking:
```bash
# Set your W&B API key as an environment variable
export WANDB_API_KEY=your_api_key
```

## Configuration

Before running the project, you may want to adjust the configuration parameters in `config.py`:

- Dataset paths
- Model parameters
- Training hyperparameters
- Output directories
- Weights & Biases project name

## Dataset Preparation

The project expects a dataset with image-caption pairs. By default, it should be organized as follows:

1. Train and test splits
2. Each split containing images and corresponding captions in Vietnamese

You can either:
- Use your own dataset by modifying the data loading functions in `data/data_processor.py`
- Use a pre-processed dataset by specifying its path with the `--dataset_path` argument

## Usage

### 1. Training the Model

To train the model from scratch:

```bash
python main.py --mode train --use_wandb
```

This will:
- Prepare the dataset (or load a pre-processed one)
- Initialize W&B tracking if the API key is set
- Load the ViT and BARTpho models
- Train the combined model on the dataset
- Save checkpoints to the specified output directory

Common training options:
```bash
# Train with a specific dataset
python main.py --mode train --dataset_path /path/to/dataset

# Force reprocessing of the dataset
python main.py --mode train --force_preprocess

# Train with a specific experiment name for tracking
python main.py --mode train --use_wandb --experiment_name my_experiment
```

### 2. Generating Captions for a Single Image

To generate a caption for a specific image:

```bash
python main.py --mode inference --image_path path/to/image.jpg
```

Options for inference:
```bash
# Use a specific checkpoint
python main.py --mode inference --image_path path/to/image.jpg --checkpoint_path path/to/checkpoint

# Adjust beam search parameters
python main.py --mode inference --image_path path/to/image.jpg --num_beams 5 --max_length 50
```

### 3. Batch Inference on Test Dataset

To run inference on the entire test dataset:

```bash
python main.py --mode batch_inference
```

This is useful for evaluating model performance across the test set. Additional options:

```bash
# Try different beam sizes and compare results
python main.py --mode batch_inference --beam_range --min_beams 1 --max_beams 5

# Use a specific checkpoint
python main.py --mode batch_inference --checkpoint_path path/to/checkpoint

# Save results to a specific directory
python main.py --mode batch_inference --output_dir ./my_results
```

## Weights & Biases Integration

The project supports Weights & Biases for experiment tracking:

1. Set up your W&B API key as an environment variable:
```bash
export WANDB_API_KEY=your_api_key
```

2. Enable W&B tracking when running the model:
```bash
python main.py --mode train --use_wandb --experiment_name my_experiment
```

If the API key is not set, W&B tracking will be automatically disabled.

## Model Evaluation

The model's performance is evaluated using standard metrics:
- BLEU score
- ROUGE score
- METEOR score
- CIDEr score

These metrics are calculated during training and are also available after batch inference.

## Extending the Project

### Using Different Models

To use different pre-trained models:
1. Modify the `load_model_and_processors` function in `models/model_config.py`
2. Adjust the tokenizer and feature extractor accordingly

### Custom Datasets

To use your own dataset:
1. Modify the data loading functions in `data/data_processor.py`
2. Ensure your dataset has the required structure (images and captions)
3. Update the dataset paths in `config.py`

## Troubleshooting

Common issues:
- **Out of memory errors**: Reduce batch size in `config.py`
- **Slow training**: Enable FP16 training by setting `USE_FP16=True` in `config.py`
- **W&B connection issues**: Check that your API key is correctly set
