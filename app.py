from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from processor import process_email_with_ai

class EmailData(BaseModel):
    email_content: Optional[str] = None

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/processar")
async def processar_email_api(data: EmailData):
    email_text = data.email_content

    if not email_text:
        raise HTTPException(status_code=400, detail="Nenhum conteúdo de email fornecido para processamento.")
    resultado = process_email_with_ai(email_text)
    return resultado

@app.post("/api/processar/upload")
async def processar_upload_api(file: UploadFile = File(None), email_content: str = Form(None)):
    email_text = ""

    if email_content:
        email_text = email_content
    elif file:
        file_extension = file.filename.split('.')[-1].lower()

        if file_extension == 'txt':
            content = await file.read()
            email_text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Formato de arquivo não suportado.")
    
    if not email_text:
        raise HTTPException(status_code=400, detail="Nenhum conteúdo de email ou arquivo fornecido para processamento.")
    
    resultado = process_email_with_ai(email_text)
    return resultado