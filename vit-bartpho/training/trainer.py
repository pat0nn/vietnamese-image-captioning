"""Training functionality for the image captioning model."""

import wandb
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments, default_data_collator
import os
import sys
sys.path.append('..')
import config 
from utils.callbacks import WandbModelCheckpointCallback, EpochTrackingCallback
from training.dataset import ImageCaptioningDataset
from training.metrics import compute_metrics

def initialize_wandb(project_name=config.WANDB_PROJECT, experiment_name=config.WANDB_NAME, api_key=None):
    """
    Initialize Weights & Biases logging.
    
    Args:
        project_name: Name of the W&B project
        experiment_name: Name of this specific experiment
        api_key: W&B API key (optional, can be loaded from environment or kaggle)
    """
    if api_key:
        wandb.login(key=api_key)
    
    wandb.init(project=project_name, name=experiment_name)
    
    return wandb.run

def setup_training(model, feature_extractor, tokenizer, dataset, metrics_calculator=None, use_wandb=False):
    """
    Set up the training components.
    
    Args:
        model: The model to train
        feature_extractor: Feature extractor for processing images
        tokenizer: Tokenizer for processing text
        dataset: Dataset dictionary with train and test splits
        metrics_calculator: Optional custom metrics calculator
        use_wandb: Whether to use Weights & Biases for logging
        
    Returns:
        trainer: Configured Seq2SeqTrainer
    """
    # Create datasets
    train_dataset = ImageCaptioningDataset(
        dataset, 'train', tokenizer, feature_extractor, config.MAX_TARGET_LENGTH)
    eval_dataset = ImageCaptioningDataset(
        dataset, 'test', tokenizer, feature_extractor, config.MAX_TARGET_LENGTH)
    
    # Log subset usage information
    if config.USE_SUBSET:
        print(f"Using subset of data for quick testing:")
        print(f"  - Training samples: {len(train_dataset)} (from {len(dataset['train'])})")
        print(f"  - Evaluation samples: {len(eval_dataset)} (from {len(dataset['test'])})")
        
        # Log to wandb if enabled
        if use_wandb:
            wandb.config.update({
                "use_subset": config.USE_SUBSET,
                "train_subset_size": len(train_dataset),
                "test_subset_size": len(eval_dataset)
            })

    # Configure report_to based on wandb availability
    report_to = "wandb" if use_wandb else "none"
    
    # Set up training arguments
    training_args = Seq2SeqTrainingArguments(
        predict_with_generate=True,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=1,
        per_device_train_batch_size=config.BATCH_SIZE,
        per_device_eval_batch_size=config.EVAL_BATCH_SIZE,
        output_dir=config.OUTPUT_DIR,
        report_to=report_to,
        fp16=config.USE_FP16,
        weight_decay=config.WEIGHT_DECAY,
        logging_dir=config.LOGS_DIR,
        logging_strategy="epoch",
        logging_steps=100,
    )
    
        # Setup compute_metrics with tokenizer and paths
    groundtruth_file = config.GROUNDTRUTH_FILE if hasattr(config, 'GROUNDTRUTH_FILE') else None
    eval_output_dir = os.path.join(config.OUTPUT_DIR, "eval")
    
    print(f"Using groundtruth file: {groundtruth_file}")
    # Configure callbacks
    
    epoch_callback = EpochTrackingCallback()
    
    callbacks = [epoch_callback]
    if use_wandb:
        callbacks.append(WandbModelCheckpointCallback())
        
    # Create custom metric function that captures the current epoch
    def metric_fn_with_epoch(eval_preds):
        return compute_metrics(
            eval_preds=eval_preds, 
            tokenizer=tokenizer,
            groundtruth_file=groundtruth_file,
            output_dir=eval_output_dir,
            dataset=eval_dataset,
            epoch=epoch_callback.current_epoch
        )
    
    # Create trainer
    trainer = Seq2SeqTrainer(
        model=model,
        tokenizer=feature_extractor,  # Required for proper image preprocessing
        args=training_args,
        compute_metrics=metric_fn_with_epoch,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=default_data_collator,
        callbacks=callbacks
    )
    
    return trainer

def train_model(trainer):
    """
    Train the model.
    
    Args:
        trainer: Configured Seq2SeqTrainer
    
    Returns:
        training_output: Output from the training process
    """
    # Start training
    training_output = trainer.train()
    
    return training_output
