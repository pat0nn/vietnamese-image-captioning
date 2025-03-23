import numpy as np
from underthesea import sent_tokenize
import evaluate
from pycocoevalcap.cider.cider import Cider

def setup_metrics():
    """Setup evaluation metrics."""
    rouge = evaluate.load("rouge")
    bleu = evaluate.load("bleu")
    return rouge, bleu

def postprocess_text(preds, labels):
    """Post-process generated and reference text for evaluation."""
    preds = [pred.strip() for pred in preds]
    labels = [label.strip() for label in labels]
    # rougeLSum expects newline after each sentence
    preds = ["\n".join(sent_tokenize(pred)) for pred in preds]
    labels = ["\n".join(sent_tokenize(label)) for label in labels]
    return preds, labels

def compute_metrics(eval_preds, tokenizer, ignore_pad_token_for_loss=True):
    """Compute evaluation metrics for the generated captions."""
    rouge, bleu = setup_metrics()
    
    preds, labels = eval_preds
    if isinstance(preds, tuple):
        preds = preds[0]

    # Flatten labels if they are nested lists
    if isinstance(labels, list) and isinstance(labels[0], list):
        labels = np.array([item for sublist in labels for item in sublist])

    # Decode predictions and labels
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    if ignore_pad_token_for_loss:
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    # Post-process text
    decoded_preds, decoded_labels = postprocess_text(decoded_preds, decoded_labels)

    # Compute metrics
    rouge_result = rouge.compute(predictions=decoded_preds, references=decoded_labels)
    bleu_result = bleu.compute(predictions=decoded_preds, references=[[label] for label in decoded_labels])

    # Calculate CIDEr score
    cider_scorer = Cider()
    cider_references = {i: [label] for i, label in enumerate(decoded_labels)}
    cider_predictions = {i: [pred] for i, pred in enumerate(decoded_preds)}
    cider_score, _ = cider_scorer.compute_score(cider_references, cider_predictions)

    # Format results
    result = {
        "rouge1": round(rouge_result["rouge1"] * 100, 4),
        "rouge2": round(rouge_result["rouge2"] * 100, 4),
        "rougeL": round(rouge_result["rougeL"] * 100, 4),
        "bleu": round(bleu_result["bleu"] * 100, 4),
        "cider": round(cider_score * 100, 4)
    }

    # Compute average length of generated texts
    prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in preds]
    result["gen_len"] = np.mean(prediction_lens)

    return result
