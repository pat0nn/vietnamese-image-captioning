import wandb
from functools import partial
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments, default_data_collator

from models.metrics import compute_metrics
from training.callbacks import WandbModelCheckpointCallback

def setup_training(model, tokenizer, train_dataset, eval_dataset, config):
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
        evaluation_strategy="epoch",
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
    
    # Setup compute_metrics with tokenizer
    metric_fn = partial(compute_metrics, tokenizer=tokenizer)
    
    # Setup callbacks
    callbacks = []
    if config.USE_WANDB and config.WANDB_SAVE_CHECKPOINT:
        callbacks.append(WandbModelCheckpointCallback())
    
    # Create trainer
    trainer = Seq2SeqTrainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        compute_metrics=metric_fn,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=default_data_collator,
        callbacks=callbacks if callbacks else None
    )
    
    return trainer

def train_model(trainer):
    """Train the model."""
    trainer.train()
    return trainer.model
