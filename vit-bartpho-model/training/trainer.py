import wandb
import os
from functools import partial
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments, default_data_collator

from models.metrics import compute_metrics
from training.callbacks import WandbModelCheckpointCallback, EpochTrackingCallback

def setup_training(model,feature_extractor, tokenizer, train_dataset, eval_dataset, config):
    """Setup training arguments and trainer."""
    # Initialize Weights & Biases if enabled
    if config.USE_WANDB:
        wandb.init(project=config.WANDB_PROJECT, name=config.WANDB_RUN_NAME)
        report_to = "wandb"
    else:
        report_to = "none"
    
    # Create training arguments
    training_args = Seq2SeqTrainingArguments(
        predict_with_generate=True,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=1,
        per_device_train_batch_size=config.BATCH_SIZE,
        per_device_eval_batch_size=config.EVAL_BATCH_SIZE,
        output_dir=config.OUTPUT_DIR,
        report_to=report_to,
        fp16=config.FP16,
        weight_decay=config.WEIGHT_DECAY,
        num_train_epochs=config.NUM_EPOCHS,
        logging_dir=config.LOGS_DIR,
        logging_strategy="epoch",
        logging_steps=100,
    )
    
    # Setup compute_metrics with tokenizer and paths
    groundtruth_file = config.GROUNDTRUTH_FILE if hasattr(config, 'GROUNDTRUTH_FILE') else None
    eval_output_dir = os.path.join(config.OUTPUT_DIR, "eval")
    
    # Create epoch tracking callback
    epoch_callback = EpochTrackingCallback()
    
    # Setup callbacks
    callbacks = [epoch_callback]  # Always include epoch callback
    if config.USE_WANDB and config.WANDB_SAVE_CHECKPOINT:
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
        tokenizer=feature_extractor,
        args=training_args,
        compute_metrics=metric_fn_with_epoch,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=default_data_collator,
        callbacks=callbacks
    )
    
    return trainer

def train_model(trainer):
    """Train the model."""
    trainer.train()
    return trainer.model
