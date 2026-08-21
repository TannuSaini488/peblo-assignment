import pytest
from fastapi import HTTPException
from app.services.artwork_service import validate_artwork
import io
from PIL import Image

def create_test_image(width, height):
    img = Image.new('RGB', (width, height), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def test_validate_artwork_valid_poster():
    img_data = create_test_image(600, 900)
    dimensions = validate_artwork("poster", img_data)
    assert dimensions["width"] == 600
    assert dimensions["height"] == 900

def test_validate_artwork_invalid_type():
    img_data = create_test_image(600, 900)
    with pytest.raises(HTTPException) as exc_info:
        validate_artwork("unknown", img_data)
    assert exc_info.value.status_code == 400

def test_validate_artwork_invalid_aspect_ratio():
    # Banner requires 16:9, giving it a 1:1 image
    img_data = create_test_image(500, 500)
    with pytest.raises(HTTPException) as exc_info:
        validate_artwork("banner", img_data)
    assert "aspect ratio" in exc_info.value.detail.lower()

def test_validate_artwork_too_large_file():
    # Create an image that passes dimension checks but we manually inject a large size
    # Since we can't easily generate a >200kb image trivially without noise, 
    # we just append bytes to the valid image data
    img_data = create_test_image(600, 900)
    large_data = img_data + b'0' * (250 * 1024)
    
    with pytest.raises(HTTPException) as exc_info:
        validate_artwork("poster", large_data)
    assert "file size" in exc_info.value.detail.lower()

def test_validate_artwork_not_an_image():
    with pytest.raises(HTTPException) as exc_info:
        validate_artwork("poster", b"this is not an image")
    assert "valid image" in exc_info.value.detail.lower()
