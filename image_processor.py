# image_processor.py
from PIL import Image, ImageEnhance
from io import BytesIO

def preprocess_image(image_bytes, file_type):
    """
    Converts the image to high-contrast grayscale to improve OCR readability.
    
    Returns: The processed image data as bytes.
    """
    
    # 1. Open the image and convert to grayscale
    img = Image.open(BytesIO(image_bytes))
    
    # Ensure it's not a PNG with a transparency layer that complicates processing
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
        
    img = img.convert('L') # Convert to Grayscale

    # 2. Enhance Contrast (Crucial for faint text)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0) # Boost contrast by 200%

    # 3. Save processed image back to BytesIO object
    output = BytesIO()
    
    # Use JPEG format for output as it's generally safe, even if input was PNG
    img.save(output, format='JPEG', quality=90) 
    
    #print("🔬 Preprocessing complete: Grayscale + 200% Contrast applied.")
    return output.getvalue()