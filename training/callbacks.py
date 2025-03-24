import os
import shutil
from transformers import TrainerCallback

class WandbModelCheckpointCallback(TrainerCallback):
    """Callback to save model checkpoints to Weights & Biases."""
    def on_save(self, args, state, control, **kwargs):
        """Save model on Wandb after each checkpoint is saved."""
        try:
            import wandb
            
            checkpoint_path = os.path.join(args.output_dir, f"checkpoint-{state.global_step}")

            # Ensure checkpoint directory exists
            if os.path.exists(checkpoint_path):
                # Save artifact to wandb
                artifact = wandb.Artifact(
                    name=f"model-checkpoint-{state.global_step}",
                    type="model",
                    description=f"Model checkpoint at step {state.global_step}"
                )
                artifact.add_dir(checkpoint_path)
                artifact.save()
                wandb.log_artifact(artifact)

                # After saving to wandb, delete local checkpoint to save space
                shutil.rmtree(checkpoint_path)
        except ImportError:
            print("Wandb is not installed or configured properly, skipping checkpoint upload.")
        except Exception as e:
            print(f"Error saving checkpoint to wandb: {str(e)}")

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
