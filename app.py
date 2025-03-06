import streamlit as st
import os
import zipfile
import tempfile
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import face_recognition
import io
import shutil
from pathlib import Path
import base64
import cv2

st.set_page_config(
    page_title="Profile Picture Generator",
    page_icon="🖼️",
    layout="wide"
)

def apply_circular_mask(img, radius):
    """Apply a circular mask to the image."""
    width, height = img.size
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, width, height), fill=255)
    
    result = img.copy()
    result.putalpha(mask)
    
    return result

def get_face_location(image_path):
    """Detect face in an image and return the face location."""
    # Load the image using face_recognition
    img = face_recognition.load_image_file(image_path)
    
    # Find all face locations in the image
    face_locations = face_recognition.face_locations(img)
    
    if not face_locations:
        return None
    
    # Return the first face location (assuming one face per image)
    # Format: (top, right, bottom, left)
    return face_locations[0]

def process_image(image_path, name, bbox_size, padding, frame_size, font_size, font_path, 
                  border_radius, text_color, align_center, top_padding, quality):
    """Process a single image to create a profile picture with name."""
    try:
        # Get face location
        face_location = get_face_location(image_path)
        
        if not face_location:
            st.warning(f"No face detected in {os.path.basename(image_path)}. Skipping...")
            return None
        
        # Extract face coordinates (top, right, bottom, left)
        top, right, bottom, left = face_location
        
        # Calculate center of the face
        face_center_x = (left + right) // 2
        face_center_y = (top + bottom) // 2
        
        # Calculate the size of the bounding box
        half_bbox = bbox_size // 2
        
        # Calculate the bounding box coordinates with padding
        bbox_left = max(0, face_center_x - half_bbox - padding)
        bbox_top = max(0, face_center_y - half_bbox - padding)
        bbox_right = face_center_x + half_bbox + padding
        bbox_bottom = face_center_y + half_bbox + padding
        
        # Open the image
        img = Image.open(image_path)
        
        # Crop the image to the bounding box
        cropped_img = img.crop((bbox_left, bbox_top, bbox_right, bbox_bottom))
        
        # Resize the cropped image to ensure it fits within the frame
        cropped_size = min(frame_size[0], frame_size[0])  # Square crop
        cropped_img = cropped_img.resize((cropped_size, cropped_size), Image.LANCZOS)
        
        # Apply border radius if specified
        if border_radius > 0:
            # Create a mask for rounded corners
            mask = Image.new('L', cropped_img.size, 0)
            draw = ImageDraw.Draw(mask)
            
            if border_radius >= cropped_size // 2:  # Circle
                draw.ellipse((0, 0, cropped_size, cropped_size), fill=255)
            else:  # Rounded rectangle
                draw.rounded_rectangle((0, 0, cropped_size, cropped_size), radius=border_radius, fill=255)
            
            # Create an empty image with RGBA mode
            result = Image.new('RGBA', cropped_img.size, (0, 0, 0, 0))
            
            # Convert cropped image to RGBA if it's not already
            if cropped_img.mode != 'RGBA':
                cropped_img = cropped_img.convert('RGBA')
            
            # Apply the mask
            result.paste(cropped_img, (0, 0), mask)
            cropped_img = result
        
        # Create a new image with the specified frame size
        frame = Image.new('RGBA', frame_size, (255, 255, 255, 255))
        
        # Calculate position to center the cropped image horizontally
        pos_x = (frame_size[0] - cropped_size) // 2
        pos_y = top_padding
        
        # Paste the cropped image into the frame
        frame.paste(cropped_img, (pos_x, pos_y), cropped_img if cropped_img.mode == 'RGBA' else None)
        
        # Add text to the frame
        draw = ImageDraw.Draw(frame)
        
        # Load font
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Calculate text width and split into multiple lines if necessary
        text_y = pos_y + cropped_size + 10
        
        # Function to wrap text
        def get_wrapped_text(text, font, max_width):
            lines = []
            words = text.split()
            current_line = words[0]
            
            for word in words[1:]:
                # Check if adding this word exceeds the max width
                test_line = current_line + " " + word
                test_width = font.getlength(test_line)
                
                if test_width <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            
            lines.append(current_line)
            return lines
        
        # Get wrapped text lines
        wrapped_lines = get_wrapped_text(name, font, frame_size[0] - 20)
        
        # Draw each line of text
        for i, line in enumerate(wrapped_lines):
            if align_center:
                text_width = font.getlength(line)
                text_x = (frame_size[0] - text_width) // 2
            else:
                text_x = 10
            
            draw.text((text_x, text_y + i * (font_size + 5)), line, fill=text_color, font=font)
        
        # Convert to RGB before saving as JPEG
        frame_rgb = frame.convert('RGB')
        
        # Save to an in-memory file
        output = io.BytesIO()
        frame_rgb.save(output, format='JPEG', quality=quality)
        output.seek(0)
        
        return output
    
    except Exception as e:
        st.error(f"Error processing {os.path.basename(image_path)}: {str(e)}")
        return None

def create_download_link(file_content, filename):
    """Create a download link for a file."""
    b64 = base64.b64encode(file_content).decode()
    href = f'<a href="data:application/zip;base64,{b64}" download="{filename}">Download Processed Images</a>'
    return href

def main():
    st.title("Automated Profile Picture Generator")
    
    st.markdown("""
    This application automatically creates profile pictures from a dataset of images and names.
    It detects faces, crops and resizes them, adds text (names), and generates downloadable profile pictures.
    """)
    
    # Create columns for better layout
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Upload Files")
        
        # File uploader for ZIP file
        uploaded_zip = st.file_uploader("Upload ZIP file containing images and CSV", type=["zip"])
        
        # File uploader for custom font
        uploaded_font = st.file_uploader("Upload custom font (optional)", type=["ttf", "otf"])
        
        st.subheader("Configuration")
        
        # Image processing parameters
        bbox_size = st.slider("Face Bounding Box Size", 20, 200, 40, help="Size of the face detection box in pixels")
        padding = st.slider("Padding", 0, 100, 40, help="Extra space around the face in pixels")
        
        # Frame parameters
        frame_width = st.slider("Frame Width", 50, 500, 100, help="Width of the output image in pixels")
        frame_height = st.slider("Frame Height", 50, 500, 160, help="Height of the output image in pixels")
        
        # Text parameters
        font_size = st.slider("Font Size", 8, 50, 16, help="Size of the text font in pixels")
        
        # Border radius for profile picture
        border_radius = st.slider("Border Radius", 0, 100, 0, 
                                 help="0 for square, higher values for rounded corners, max for circle")
        
        # Text color
        text_color = st.color_picker("Text Color", "#000000")
        
        # Alignment
        align_center = st.checkbox("Center Align Text", value=True)
        
        # Top padding
        top_padding = st.slider("Top Padding", 0, 100, 10, help="Space from the top of the frame to the profile picture")
        
        # Output quality
        quality = st.slider("JPEG Quality", 1, 100, 90, help="Quality of the output JPEG images")
    
    # Information about the expected input format
    with col2:
        st.subheader("How to Prepare Your Data")
        
        st.markdown("""
        ### Expected Input Format
        
        1. **CSV File**: A file named `names.csv` with one column containing names (e.g., "John Doe")
        2. **Images**: Named numerically (e.g., `1.jpg`, `2.jpg`), corresponding to rows in the CSV
        3. **ZIP File**: Contains both the CSV file and images folder
        
        ### Example Structure:
        ```
        mydata.zip
        ├── names.csv
        └── images/
            ├── 1.jpg
            ├── 2.jpg
            └── 3.jpg
        ```
        
        ### Sample CSV:
        ```
        Name
        John Doe
        Jane Smith
        Alex Johnson
        ```
        """)
        
        # If files are uploaded, show sample processing
        if uploaded_zip is not None:
            st.subheader("Processing")
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract ZIP file
                with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Try to find the CSV file
                csv_files = list(Path(temp_dir).glob('**/*.csv'))
                
                if not csv_files:
                    st.error("No CSV file found in the uploaded ZIP. Please include a CSV file with names.")
                else:
                    # Use the first CSV file found
                    csv_file = csv_files[0]
                    
                    # Try to read the CSV file
                    try:
                        df = pd.read_csv(csv_file)
                        
                        # Check if the CSV has at least one column
                        if df.shape[1] < 1:
                            st.error("CSV file doesn't have any columns. Please include a column with names.")
                        else:
                            # Use the first column for names
                            names_column = df.iloc[:, 0]
                            
                            # Find image files
                            image_files = []
                            for ext in ['jpg', 'jpeg', 'png']:
                                image_files.extend(list(Path(temp_dir).glob(f'**/*.{ext}')))
                                image_files.extend(list(Path(temp_dir).glob(f'**/*.{ext.upper()}')))
                            
                            if not image_files:
                                st.error("No image files found in the uploaded ZIP. Please include images.")
                            else:
                                # Sort image files to match CSV order if possible
                                try:
                                    image_files.sort(key=lambda x: int(x.stem))
                                except:
                                    # If images can't be sorted numerically, use alphabetical sort
                                    image_files.sort()
                                
                                # Handle font file
                                font_path = None
                                if uploaded_font is not None:
                                    font_temp = os.path.join(temp_dir, "custom_font" + 
                                                        os.path.splitext(uploaded_font.name)[1])
                                    with open(font_temp, "wb") as f:
                                        f.write(uploaded_font.getbuffer())
                                    font_path = font_temp
                                else:
                                    # Use default font
                                    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                        "assets", "arial.ttf")
                                    if not os.path.exists(font_path):
                                        # Fallback to system default
                                        font_path = None
                                
                                # Sample processing for preview
                                if st.button("Generate Preview"):
                                    if len(image_files) > 0 and len(names_column) > 0:
                                        # Process the first image for preview
                                        frame_size = (frame_width, frame_height)
                                        preview_img = process_image(
                                            str(image_files[0]), 
                                            names_column[0],
                                            bbox_size,
                                            padding,
                                            frame_size,
                                            font_size,
                                            font_path,
                                            border_radius,
                                            text_color,
                                            align_center,
                                            top_padding,
                                            quality
                                        )
                                        
                                        if preview_img:
                                            st.image(preview_img, caption=f"Preview: {names_column[0]}", 
                                                    use_column_width=True)
                                        else:
                                            st.warning("Could not generate preview. Please check your image.")
                                
                                # Process all images button
                                if st.button("Process All Images"):
                                    progress_bar = st.progress(0)
                                    status_text = st.empty()
                                    
                                    # Create a temporary ZIP file to store processed images
                                    zip_buffer = io.BytesIO()
                                    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                                        # Process each image
                                        total_images = min(len(image_files), len(names_column))
                                        processed_count = 0
                                        
                                        for i in range(total_images):
                                            if i < len(image_files) and i < len(names_column):
                                                status_text.text(f"Processing image {i+1}/{total_images}: {names_column[i]}")
                                                
                                                # Process image
                                                frame_size = (frame_width, frame_height)
                                                processed_img = process_image(
                                                    str(image_files[i]), 
                                                    names_column[i],
                                                    bbox_size,
                                                    padding,
                                                    frame_size,
                                                    font_size,
                                                    font_path,
                                                    border_radius,
                                                    text_color,
                                                    align_center,
                                                    top_padding,
                                                    quality
                                                )
                                                
                                                if processed_img:
                                                    # Add to ZIP
                                                    zip_file.writestr(
                                                        f"{i+1:02d}.jpg", 
                                                        processed_img.getvalue()
                                                    )
                                                    processed_count += 1
                                                
                                                # Update progress
                                                progress_bar.progress((i + 1) / total_images)
                                        
                                        status_text.text(f"Processing complete! {processed_count}/{total_images} images processed.")
                                    
                                    # Provide download link
                                    zip_buffer.seek(0)
                                    st.success("All images processed successfully!")
                                    st.markdown(create_download_link(zip_buffer.getvalue(), "processed_images.zip"), 
                                            unsafe_allow_html=True)
                                    
                    except Exception as e:
                        st.error(f"Error reading CSV file: {str(e)}")
    
    # Instructions and FAQ
    st.subheader("Instructions & FAQ")
    
    with st.expander("How to use this tool?"):
        st.markdown("""
        1. Prepare a ZIP file containing your images and a CSV file with names.
        2. Upload the ZIP file using the file uploader.
        3. Optionally, upload a custom font file.
        4. Adjust the settings as needed.
        5. Click "Generate Preview" to see a sample of the output.
        6. Click "Process All Images" to process all images.
        7. Download the resulting ZIP file with processed images.
        """)
    
    with st.expander("Troubleshooting"):
        st.markdown("""
        - **No face detected**: Ensure the images contain clearly visible faces.
        - **CSV format issues**: Make sure your CSV file has a header row and contains names in the first column.
        - **Font problems**: If text doesn't display correctly, try uploading a custom font that supports your language.
        """)

    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2023 Profile Picture Generator")

if __name__ == "__main__":
    main() 