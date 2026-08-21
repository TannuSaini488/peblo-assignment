import json
import io
from PIL import Image, UnidentifiedImageError
from fastapi import HTTPException
from app.config import settings

def load_reference_data():
    try:
        with open("reference.json") as f:
            return json.load(f)
    except FileNotFoundError:
        with open("../reference.json") as f:
            return json.load(f)

reference_data = load_reference_data()
ARTWORK_SPECS = reference_data.get("artwork_specs", {})

def validate_artwork(artwork_type: str, file_data: bytes) -> dict:
    """
    Validates artwork according to specifications.
    Raises HTTPException with a human-readable error if validation fails.
    Returns parsed dimensions.
    """
    if artwork_type not in ARTWORK_SPECS:
        raise HTTPException(status_code=400, detail=f"Invalid artwork type: {artwork_type}")
    
    spec = ARTWORK_SPECS[artwork_type]
    
    # 1. File size check
    file_size_kb = len(file_data) / 1024
    if file_size_kb > spec["max_kb"]:
        raise HTTPException(
            status_code=400, 
            detail=f"{artwork_type.title()} file size must be under {spec['max_kb']} KB. Uploaded file is {file_size_kb:.1f} KB."
        )

    # 2. Check if valid image
    try:
        img = Image.open(io.BytesIO(file_data))
        img.verify() # Verify it's a valid image without decoding everything
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400, 
            detail=f"The uploaded file is not a valid image."
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error reading image: {str(e)}"
        )

    # Re-open to get dimensions since verify() might close it or alter state
    img = Image.open(io.BytesIO(file_data))
    width, height = img.size
    
    if width == 0 or height == 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Image dimensions are invalid."
        )

    # 3. Aspect ratio check (± 5% tolerance)
    actual_aspect = width / height
    
    aspect_str = spec["aspect"]
    aspect_parts = aspect_str.split(":")
    expected_aspect = int(aspect_parts[0]) / int(aspect_parts[1])
    
    if abs(actual_aspect - expected_aspect) / expected_aspect > 0.05:
        raise HTTPException(
            status_code=400, 
            detail=f"{artwork_type.title()} must use a {aspect_str} aspect ratio. Uploaded image is {width}x{height}."
        )
        
    # 4. Dimensions check (± 15% tolerance)
    expected_width, expected_height = spec["target_px"]
    width_diff = abs(width - expected_width) / expected_width
    height_diff = abs(height - expected_height) / expected_height
    
    if width_diff > 0.15 or height_diff > 0.15:
        raise HTTPException(
            status_code=400,
            detail=f"{artwork_type.title()} must be approximately {expected_width}x{expected_height}. Uploaded image is {width}x{height}."
        )

    return {
        "width": width,
        "height": height,
        "size_bytes": len(file_data)
    }
