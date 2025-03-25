import numpy as np
import json
import os
from underthesea import sent_tokenize
import evaluate
import metrics

def load_groundtruth_ids(groundtruth_file):
    """Load image IDs from groundtruth file."""
    if not groundtruth_file or not os.path.exists(groundtruth_file):
        return None
    
    try:
        with open(groundtruth_file, 'r', encoding='utf-8') as f:
            gt_data = json.load(f)
        return list(gt_data.keys())
    except Exception as e:
        print(f"Error loading groundtruth IDs: {e}")
        return None

def save_predictions_to_json(predictions, image_ids, output_file, groundtruth_file=None):
    """
    Save predictions to a JSON file with image IDs as keys.
    If image_ids is not provided, tries to use groundtruth_file to align IDs.
    """
    predictions_dict = {}
    
    # If image_ids not provided but groundtruth_file is available, use its IDs
    if (image_ids is None or len(image_ids) == 0) and groundtruth_file:
        image_ids = load_groundtruth_ids(groundtruth_file)
    
    
    # Map predictions to image IDs

    for i, pred in enumerate(predictions):
        predictions_dict[image_ids[i]] = pred
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(predictions_dict, f, ensure_ascii=False, indent=2)
    
    print(f"Saved predictions to {output_file} with {len(predictions_dict)} entries")
    return output_file

def evaluate_from_files(groundtruth_file, prediction_file):
    """
    Đánh giá các tham số dựa trên hai file đầu vào.
    
    Args:
        groundtruth_file (str): Đường dẫn đến file chứa groundtruth caption
        prediction_file (str): Đường dẫn đến file chứa kết quả caption
        
    Returns:
        dict: Kết quả đánh giá các tham số
    """
    # Đọc file groundtruth caption
    # print(f"Đọc file groundtruth từ: {groundtruth_file}")
    with open(groundtruth_file, 'r', encoding='utf-8') as f:
        gt_data = json.load(f)
    
    # Đọc file prediction caption
    # print(f"Đọc file prediction từ: {prediction_file}")
    with open(prediction_file, 'r', encoding='utf-8') as f:
        pred_data = json.load(f)
        
    # print(pred_data)
    
    # Chuẩn bị dữ liệu cho việc tính toán metrics
    gt_captions = {}
    pred_captions = {}
    
    # Chuyển đổi dữ liệu groundtruth
    for image_id, captions in gt_data.items():
        gt_captions[image_id] = captions if isinstance(captions, list) else [captions]
    
    # Chuyển đổi dữ liệu prediction
    for image_id, caption in pred_data.items():
        if isinstance(caption, str):
            pred_captions[image_id] = [caption]
        elif isinstance(caption, list):
            pred_captions[image_id] = caption
        else:
            print(f"Warning: Không nhận dạng được định dạng caption cho image_id {image_id}")
    
    # Kiểm tra các image_id chung
    gt_ids = set(gt_captions.keys())
    pred_ids = set(pred_captions.keys())
    common_ids = gt_ids.intersection(pred_ids)
    
    # if len(common_ids) == 0:
    #     print("CẢNH BÁO: Không tìm thấy image_id chung giữa hai file!")
    #     return {}
    
    # print(f"Số lượng image trong groundtruth: {len(gt_ids)}")
    # print(f"Số lượng image trong prediction: {len(pred_ids)}")
    # print(f"Số lượng image chung để đánh giá: {len(common_ids)}")
    
    # if len(common_ids) < len(gt_ids) or len(common_ids) < len(pred_ids):
    #     print(f"Cảnh báo: Có {len(gt_ids) - len(common_ids)} ảnh từ groundtruth không có trong prediction")
    #     print(f"Cảnh báo: Có {len(pred_ids) - len(common_ids)} ảnh từ prediction không có trong groundtruth")
    
    # Lọc để chỉ giữ các image_id chung
    filtered_gt = {id: gt_captions[id] for id in common_ids}
    filtered_pred = {id: pred_captions[id] for id in common_ids}
    
    # Tính toán các metrics
    print("Computing metrics...")
    scores = metrics.compute_scores(filtered_gt, filtered_pred)[0]
    
    result = {}
    for metric, score in scores.items():
        if metric == "BLEU":
            result["BLEU-1"] = score[0]
            result["BLEU-2"] = score[1]
            result["BLEU-3"] = score[2]
            result["BLEU-4"] = score[3]
        else:
            result[metric] = score
    
    
    
    return result
    

def compute_metrics(eval_preds, tokenizer, ignore_pad_token_for_loss=True, groundtruth_file=None, output_dir=None, dataset=None, epoch=None):
    """Compute evaluation metrics for the generated captions."""
    preds, labels = eval_preds
    
    # print(f"Predictions shape: {preds.shape}")
    # if isinstance(preds, tuple):
    #     preds = preds[0]

    # Decode predictions
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    
    # print(f"Decoded predictions: {decoded_preds}")
    
    # Save predictions to a JSON file
    if output_dir is None:
        output_dir = "./eval_outputs"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Include epoch number in filename if available
    if epoch is not None:
        prediction_file = os.path.join(output_dir, f"predictions_epoch_{epoch}.json")
    else:
        prediction_file = os.path.join(output_dir, "predictions.json")
    
    image_ids=None
    save_predictions_to_json(decoded_preds, image_ids, prediction_file, groundtruth_file)
    
    # If groundtruth file is provided, evaluate metrics
    if groundtruth_file and os.path.exists(groundtruth_file):
        result = evaluate_from_files(groundtruth_file, prediction_file)
    else:
        result = {}
    
    return result
