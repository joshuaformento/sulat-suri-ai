from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.essays import router as essay_router
import uvicorn

app = FastAPI(
    title="Essay AI API",
    description="API for essay analysis and processing",
    version="1.0.0" 
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Essay AI API"}

app.include_router(essay_router, prefix='/api/v1')

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 