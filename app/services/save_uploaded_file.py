import os
from fastapi import UploadFile


# To Do: Save to S3
async def save_uploaded_file(uploaded_file: UploadFile, save_dir="temp_uploads"):
    """Save uploaded file temporarily and return the path"""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_path = os.path.join(save_dir, uploaded_file.filename)
    content = await uploaded_file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path