from fastapi import APIRouter, HTTPException, UploadFile, Form, File
from typing import List, Dict
from services.load_document import load_document
from services.grade_essay import grade_essay
from services.save_uploaded_file import save_uploaded_file
import json


router = APIRouter(prefix="/essays", tags=["essays"])

@router.post("/")
async def create_essay(
    essays: List[UploadFile],
    rubrics: str = Form(...)
):
    try:
        rubrics_dict = json.loads(rubrics)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid rubriks JSON format")

    # Validate required rubriks
    if not essays or not rubrics_dict:
        raise HTTPException(
            status_code=400, 
            detail="Essay files and grading criteria are required."
        )
    
    try:
        grades = []
        for file in essays:
            if not file.filename.endswith(('.pdf', '.docx', '.txt')):
                raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF, DOCX, and TXT are allowed.")
            
            document_filepath = await save_uploaded_file(file)
            document_content = await load_document(document_filepath)
            text_content = document_content[0].page_content if document_content else ""
            
            grade = await grade_essay(
                document_text=text_content,
                rubriks=rubrics_dict
            )
            
            print('Grade:', grade)
            grades.append({
                "grade": grade
            })            
        
        return {
            "message": "Essay graded successfully",
            "grades": grades
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
