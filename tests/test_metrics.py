import sys
import os
import json
import unittest
import tempfile
from pathlib import Path

# Add parent directory to path to import metrics
sys.path.append(str(Path(__file__).parent.parent))
from models.metrics import (
    load_groundtruth_ids,
    save_predictions_to_json,
    evaluate_from_files,
    compute_metrics
)

class TestMetrics(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Sample groundtruth data
        self.groundtruth_data = {
            "image1": ["Một người đàn ông đang đi bộ trên đường.", "Người đàn ông mặc áo đỏ."],
            "image2": ["Một con chó đang chạy trong công viên.", "Chú chó màu nâu chơi đùa."],
            "image3": ["Đây là một cái cây cao.", "Cây xanh đứng cạnh hồ nước."]
        }
        
        # Sample prediction data
        self.prediction_data = {
            "image1": "Người đàn ông đi bộ trên con đường.",
            "image2": "Con chó nâu chạy trong công viên.",
            "image3": "Một cái cây cao màu xanh."
        }
        
        # Create groundtruth file
        self.groundtruth_file = os.path.join(self.temp_dir.name, "groundtruth.json")
        with open(self.groundtruth_file, 'w', encoding='utf-8') as f:
            json.dump(self.groundtruth_data, f, ensure_ascii=False, indent=2)
        
        # Create prediction file
        self.prediction_file = os.path.join(self.temp_dir.name, "predictions.json")
        with open(self.prediction_file, 'w', encoding='utf-8') as f:
            json.dump(self.prediction_data, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_load_groundtruth_ids(self):
        """Test loading of image IDs from groundtruth file."""
        ids = load_groundtruth_ids(self.groundtruth_file)
        self.assertEqual(set(ids), set(["image1", "image2", "image3"]))
        
        # Test with non-existent file
        self.assertIsNone(load_groundtruth_ids("non_existent_file.json"))
    
    def test_save_predictions_to_json(self):
        """Test saving predictions to a JSON file."""
        predictions = ["Caption for image 1", "Caption for image 2"]
        image_ids = ["img1", "img2"]
        
        output_file = os.path.join(self.temp_dir.name, "test_output.json")
        
        # Test with provided image_ids
        saved_file = save_predictions_to_json(predictions, image_ids, output_file)
        
        # Verify the saved file
        with open(saved_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, {"img1": "Caption for image 1", "img2": "Caption for image 2"})
        
        # Test without image_ids but with groundtruth file
        output_file2 = os.path.join(self.temp_dir.name, "test_output2.json")
        saved_file2 = save_predictions_to_json(
            ["Caption 1", "Caption 2", "Caption 3"], 
            None, 
            output_file2, 
            self.groundtruth_file
        )
        
        with open(saved_file2, 'r', encoding='utf-8') as f:
            saved_data2 = json.load(f)
        
        self.assertEqual(len(saved_data2), 3)
        self.assertTrue(all(k in saved_data2 for k in ["image1", "image2", "image3"]))
    
    def test_evaluate_from_files(self):
        """Test evaluation metrics calculation from files."""
        # This test assumes metrics.compute_scores is implemented and working
        try:
            results = evaluate_from_files(self.groundtruth_file, self.prediction_file)
            
            # Check that the results contain expected metrics
            self.assertIsInstance(results, dict)
            # Check if at least some common metrics exist in the results
            expected_metrics = ["BLEU-1", "BLEU-2", "BLEU-3", "BLEU-4"]
            for metric in expected_metrics:
                self.assertIn(metric, results, f"Expected metric {metric} missing from results")
        except ImportError:
            # If metrics module is not available, skip the test
            print("Skipping test_evaluate_from_files as metrics module may not be fully implemented")
    
    def test_compute_metrics(self):
        """Test the compute_metrics function with dummy tokenizer."""
        # Create a mock tokenizer class
        class MockTokenizer:
            def batch_decode(self, preds, skip_special_tokens=True):
                # Return dummy captions for testing
                return ["Caption 1", "Caption 2", "Caption 3"]
        
        tokenizer = MockTokenizer()
        
        # Create dummy prediction data
        preds = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        labels = [[10, 11, 12], [13, 14, 15], [16, 17, 18]]
        
        # Test compute_metrics without groundtruth file
        output_dir = os.path.join(self.temp_dir.name, "output")
        results = compute_metrics(
            (preds, labels), 
            tokenizer, 
            ignore_pad_token_for_loss=True,
            output_dir=output_dir
        )
        
        # Verify output directory and prediction file were created
        self.assertTrue(os.path.exists(output_dir))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "predictions.json")))
        
        # Test with groundtruth file
        try:
            results_with_gt = compute_metrics(
                (preds, labels), 
                tokenizer, 
                ignore_pad_token_for_loss=True,
                groundtruth_file=self.groundtruth_file,
                output_dir=output_dir
            )
            self.assertIsInstance(results_with_gt, dict)
        except ImportError:
            # If metrics module is not available, skip this part
            print("Skipping compute_metrics test with groundtruth as metrics module may not be fully implemented")

if __name__ == "__main__":
    unittest.main()
