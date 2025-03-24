import base64
import io
from PIL import Image

def encode_image_to_base64(image_file):
    """
    Encode an image file to base64 string
    
    Args:
        image_file: The uploaded image file
        
    Returns:
        str: Base64 encoded string of the image
    """
    if hasattr(image_file, 'read'):
        # For file-like objects
        image_content = image_file.read()
    else:
        # For filepath strings
        with open(image_file, "rb") as f:
            image_content = f.read()
            
    return base64.b64encode(image_content).decode("utf-8")

def resize_image(image, max_width=800):
    """
    Resize an image while maintaining aspect ratio
    
    Args:
        image: PIL Image object
        max_width: Maximum width for the resized image
        
    Returns:
        PIL.Image: Resized image
    """
    if image.width > max_width:
        ratio = max_width / image.width
        new_height = int(image.height * ratio)
        return image.resize((max_width, new_height), Image.LANCZOS)
    return image

def validate_image(file, supported_formats, max_size):
    """
    Validate if the uploaded file is a valid image with the correct format and size
    
    Args:
        file: The uploaded file
        supported_formats: List of supported image formats
        max_size: Maximum file size in bytes
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        # Check file size
        if file.size > max_size:
            return False, f"File size exceeds the limit of {max_size/1024/1024}MB"
        
        # Check file format
        file_extension = file.name.split(".")[-1].lower()
        if file_extension not in supported_formats:
            return False, f"Unsupported file format. Please upload {', '.join(supported_formats)}"
        
        # Verify the file can be opened as an image
        image = Image.open(file)
        image.verify()
        
        return True, ""
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"