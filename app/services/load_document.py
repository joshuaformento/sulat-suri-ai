from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import Docx2txtLoader, TextLoader, PyPDFLoader

async def load_document(file_path: str) -> List[Document]:
        """
        Asynchronously load a document from file path using appropriate loader.
        
        Args:
            file_path (str): Path to the document file
            
        Returns:
            List[Document]: List of document pages/sections
        """
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.pdf':
                loader = PyPDFLoader(file_path=file_path)
                documents = await loader.aload()  # Use async loading for PDFs
        # Use async loading for images
            elif file_extension == '.docx':
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
            elif file_extension == '.txt':
                loader = TextLoader(file_path)
                documents = loader.load()
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            if not documents:
                raise ValueError(f"No content found in {file_path}")
                
            return documents
            
        except Exception as e:
            print(f"Error loading document: {str(e)}")
            raise e