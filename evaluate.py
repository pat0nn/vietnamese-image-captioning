import os
import argparse
import json
import numpy as np
import torch
from tqdm import tqdm
import metrics
import time

def evaluate_from_files(
    groundtruth_file,
    prediction_file,
):
    """
    Đánh giá các tham số dựa trên hai file đầu vào.
    
    Args:
        groundtruth_file (str): Đường dẫn đến file chứa groundtruth caption
        prediction_file (str): Đường dẫn đến file chứa kết quả caption
        
    Returns:
        dict: Kết quả đánh giá các tham số
    """
    # Đọc file groundtruth caption
    print(f"Đọc file groundtruth từ: {groundtruth_file}")
    with open(groundtruth_file, 'r', encoding='utf-8') as f:
        gt_data = json.load(f)
    
    # Đọc file prediction caption
    print(f"Đọc file prediction từ: {prediction_file}")
    with open(prediction_file, 'r', encoding='utf-8') as f:
        pred_data = json.load(f)
    
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
    
    if len(common_ids) == 0:
        print("CẢNH BÁO: Không tìm thấy image_id chung giữa hai file!")
        return {}
    
    print(f"Số lượng image trong groundtruth: {len(gt_ids)}")
    print(f"Số lượng image trong prediction: {len(pred_ids)}")
    print(f"Số lượng image chung để đánh giá: {len(common_ids)}")
    
    if len(common_ids) < len(gt_ids) or len(common_ids) < len(pred_ids):
        print(f"Cảnh báo: Có {len(gt_ids) - len(common_ids)} ảnh từ groundtruth không có trong prediction")
        print(f"Cảnh báo: Có {len(pred_ids) - len(common_ids)} ảnh từ prediction không có trong groundtruth")
    
    # Lọc để chỉ giữ các image_id chung
    filtered_gt = {id: gt_captions[id] for id in common_ids}
    filtered_pred = {id: pred_captions[id] for id in common_ids}
    
    # Tính toán các metrics
    print("Tính toán các metrics...")
    scores = metrics.compute_scores(filtered_gt, filtered_pred)[0]
    
    print("\n===== KẾT QUẢ ĐÁNH GIÁ =====")
    for metric, score in scores.items():
        print(f"{metric}: {score}")



if __name__ == "__main__":

    gt = r"/run/media/trong/New Volume/Algo/KTVIC/processed_ktvic/grouped_captions.json"
    pred = r"/run/media/trong/New Volume/Algo/image_captioning_with_transformer/evaluate/result_BARTpho_train-test_3-21_numBeam3_converted.json"
    
    
    # Kiểm tra file tồn tại
    if not os.path.exists(gt):
        raise FileNotFoundError(f"Không tìm thấy file groundtruth: {gt}")
    
    if not os.path.exists(pred):
        raise FileNotFoundError(f"Không tìm thấy file prediction: {pred}")
    
    evaluate_from_files(gt, pred)
    
        
        
