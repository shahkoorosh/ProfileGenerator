import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import zipfile
import pandas as pd
from PIL import Image
import numpy as np
import io

# Add the parent directory to the path so we can import app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions from app.py
from app import get_face_location, apply_circular_mask, process_image

class TestProfilePictureGenerator(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a test image (100x100 white image)
        self.test_image_path = os.path.join(self.temp_dir.name, "test_image.jpg")
        img = Image.new('RGB', (100, 100), color='white')
        img.save(self.test_image_path)
        
        # Create a test CSV file
        self.test_csv_path = os.path.join(self.temp_dir.name, "test_names.csv")
        df = pd.DataFrame({"Name": ["Test Name"]})
        df.to_csv(self.test_csv_path, index=False)
        
        # Create a test ZIP file
        self.test_zip_path = os.path.join(self.temp_dir.name, "test_data.zip")
        with zipfile.ZipFile(self.test_zip_path, 'w') as zipf:
            zipf.write(self.test_image_path, arcname="1.jpg")
            zipf.write(self.test_csv_path, arcname="names.csv")
    
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    @patch('app.face_recognition')
    def test_get_face_location(self, mock_face_recognition):
        """Test the get_face_location function."""
        # Mock face_recognition to return a face location
        mock_face_recognition.load_image_file.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_face_recognition.face_locations.return_value = [(10, 60, 70, 20)]  # (top, right, bottom, left)
        
        # Call the function
        result = get_face_location(self.test_image_path)
        
        # Check the result
        self.assertEqual(result, (10, 60, 70, 20))
        
        # Test when no face is detected
        mock_face_recognition.face_locations.return_value = []
        result = get_face_location(self.test_image_path)
        self.assertIsNone(result)
    
    def test_apply_circular_mask(self):
        """Test the apply_circular_mask function."""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='white')
        
        # Apply circular mask
        result = apply_circular_mask(img, 50)
        
        # Check that the result is an image with alpha channel
        self.assertEqual(result.mode, 'RGBA')
        
        # Check dimensions
        self.assertEqual(result.size, (100, 100))
    
    @patch('app.get_face_location')
    @patch('app.ImageFont')
    def test_process_image(self, mock_image_font, mock_get_face_location):
        """Test the process_image function."""
        # Mock face detection
        mock_get_face_location.return_value = (10, 60, 70, 20)  # (top, right, bottom, left)
        
        # Mock font
        mock_font = MagicMock()
        mock_font.getlength.return_value = 50
        mock_image_font.truetype.return_value = mock_font
        
        # Call the function
        result = process_image(
            self.test_image_path,
            "Test Name",
            40,  # bbox_size
            20,  # padding
            (100, 160),  # frame_size
            16,  # font_size
            None,  # font_path
            0,  # border_radius
            "#000000",  # text_color
            True,  # align_center
            10,  # top_padding
            90  # quality
        )
        
        # Check that the result is a BytesIO object
        self.assertIsInstance(result, io.BytesIO)
        
        # Test when no face is detected
        mock_get_face_location.return_value = None
        
        # This should return None
        with patch('app.st.warning') as mock_warning:
            result = process_image(
                self.test_image_path,
                "Test Name",
                40,
                20,
                (100, 160),
                16,
                None,
                0,
                "#000000",
                True,
                10,
                90
            )
            self.assertIsNone(result)
            mock_warning.assert_called_once()

if __name__ == '__main__':
    unittest.main() 