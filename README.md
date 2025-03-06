# Automated Profile Picture Generator

A Streamlit web application that automates the creation of profile pictures from a dataset of images and names. It processes images by detecting faces, cropping and resizing them, adding text (names), and generating a downloadable ZIP file of the final profile pictures.

## Features

- **Batch Processing**: Process multiple images in one go
- **Dynamic Customization**: Adjust settings like bounding box size, padding, font size, and frame size
- **Live Preview**: Preview the output for one image before processing the entire batch
- **Farsi Support**: Support for Farsi text with custom font upload
- **ZIP Upload/Download**: Upload a ZIP file with images and CSV, download a ZIP file with processed images
- **Output Format**: Save images as JPEG with adjustable quality

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/profile-picture-generator.git
   cd profile-picture-generator
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run app.py
   ```

## How to Use

1. **Prepare Your Data**:
   - Create a CSV file with one column containing names (e.g., "John Doe")
   - Name your images numerically (e.g., `1.jpg`, `2.jpg`), corresponding to rows in the CSV
   - Compress both the CSV file and images into a ZIP file

2. **Upload Your Data**:
   - Upload the ZIP file using the file uploader
   - Optionally, upload a custom font file (TTF or OTF)

3. **Customize Settings**:
   - Adjust the face bounding box size, padding, frame dimensions, etc.
   - Choose text color, alignment, and other formatting options

4. **Generate Preview**:
   - Click "Generate Preview" to see a sample of the output

5. **Process All Images**:
   - Click "Process All Images" to process the entire batch
   - Download the resulting ZIP file with processed images

## Requirements

- Python 3.7+
- Streamlit
- Pandas
- NumPy
- Pillow (PIL)
- face-recognition
- OpenCV

## Troubleshooting

- **No face detected**: Ensure the images contain clearly visible faces
- **CSV format issues**: Make sure your CSV file has a header row and contains names in the first column
- **Font problems**: If text doesn't display correctly, try uploading a custom font that supports your language

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Face detection powered by the face-recognition library
- Image processing with Pillow and OpenCV
- Web interface built with Streamlit 