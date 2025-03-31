"""Custom callbacks for model training and evaluation."""

import os
import shutil
import wandb
from transformers import TrainerCallback

class WandbModelCheckpointCallback(TrainerCallback):
    """
    Custom callback to upload model checkpoints to Weights & Biases.
    This saves disk space by removing checkpoints from local storage
    after they've been uploaded.
    """
    
    def on_save(self, args, state, control, **kwargs):
        """
        Called when a checkpoint is saved.
        
        Args:
            args: TrainingArguments
            state: TrainerState
            control: TrainerControl
            **kwargs: Additional arguments
            
        Returns:
            control: TrainerControl
        """
        checkpoint_path = os.path.join(args.output_dir, f"checkpoint-{state.global_step}")
        
        # Ensure the checkpoint directory exists
        if os.path.exists(checkpoint_path):
            # Create and save wandb artifact
            artifact = wandb.Artifact(
                name=f"model-checkpoint-{state.global_step}", 
                type="model",
                description=f"Model checkpoint at step {state.global_step}"
            )
            artifact.add_dir(checkpoint_path)
            artifact.save()
            wandb.log_artifact(artifact)
            
            # After uploading to wandb, remove the local checkpoint to save space
            shutil.rmtree(checkpoint_path)
        
        return control


class EpochTrackingCallback(TrainerCallback):
    """
    Callback to track epoch numbers and provide them to the evaluation function.
    """
    def __init__(self):
        self.current_epoch = 0
    
    def on_epoch_begin(self, args, state, control, **kwargs):
        """Called at the beginning of each epoch"""
        # Update current epoch
        if state.epoch is not None:
            self.current_epoch = int(state.epoch)
        else:
            self.current_epoch += 1
        
        print(f"Starting epoch {self.current_epoch}")
    
    def on_evaluate(self, args, state, control, **kwargs):
        """Called before evaluation begins"""
        # Provide the current epoch number to the trainer
        trainer = kwargs.get("trainer", None)
        if trainer is not None:
            # Store current epoch in trainer's state
            trainer.current_epoch = self.current_epoch
            print(f"Evaluation at epoch {self.current_epoch}")
