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
