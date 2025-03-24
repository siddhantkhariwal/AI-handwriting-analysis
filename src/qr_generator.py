import qrcode
from PIL import Image
import io
import base64

def generate_qr_code(url, logo_path=None):
    """
    Generate a QR code with an optional logo in the center
    
    Args:
        url: The URL to encode in the QR code
        logo_path: Optional path to a logo image to place in the center
        
    Returns:
        str: Base64 encoded image of the QR code
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    # Add data to the QR code
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create an image from the QR code with a white background
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
    
    # Add logo to the center if provided
    if logo_path:
        try:
            logo = Image.open(logo_path).convert('RGBA')
            
            # Calculate logo size (max 30% of QR code)
            logo_max_size = qr_img.size[0] // 3
            if logo.size[0] > logo_max_size:
                logo_ratio = logo_max_size / logo.size[0]
                logo = logo.resize((logo_max_size, int(logo.size[1] * logo_ratio)))
            
            # Calculate position for the center
            pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
            
            # Paste the logo
            qr_img.paste(logo, pos, logo)
        except Exception as e:
            print(f"Error adding logo to QR code: {str(e)}")
    
    # Convert to base64 for embedding in HTML
    buffered = io.BytesIO()
    qr_img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str