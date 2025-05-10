from fastapi import APIRouter, HTTPException, UploadFile, Form, File
from typing import List
from services.load_document import load_document
from services.grade_essay import grade_essay
from services.save_uploaded_file import save_uploaded_file


router = APIRouter(prefix="/essays", tags=["essays"])

@router.post("/")
async def create_essay(
    essays: List[UploadFile],
    coherence: str = Form(...),
    grammar: str = Form(...),
    relevance: str = Form(...),
    reference: UploadFile = File(...)
):
    if not essays or not coherence or not grammar or not relevance:
        raise HTTPException(status_code=400, detail="Essay file and grading criteria are required.")
    
    try:
        reference_filepath = await save_uploaded_file(reference)
        reference_content = await load_document(reference_filepath)


        
        grades = []
        for file in essays:
            if not file.filename.endswith(('.pdf', '.docx', '.txt')):
                raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF, DOCX, and TXT are allowed.")
            # Save the uploaded file
            document_filepath = await save_uploaded_file(file)
            
            # Load the document content
            document_content = await load_document(document_filepath)
            
            
            # Get the text content from the first document (assuming single document)
            text_content = document_content[0].page_content if document_content else ""
            
            # Grade the essay based on the provided criteria
            grade = await grade_essay(text_content, coherence, grammar, relevance,reference_content)
            
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
