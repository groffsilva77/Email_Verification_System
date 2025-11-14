import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pypdf import PdfReader
import io
from processor import process_email_with_ai

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Lê o arquivo index.html e o retorna como uma resposta HTML explícita, forçando o navegador a renderizar."""
    try:
        html_path = os.path.join("static", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="O arquivo static/index.html não foi encontrado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar o frontend: {e}")

@app.post("/api/processar")
async def processar_upload_api(file: UploadFile = File(None), email_content: str = Form(None)):
    email_text = ""

    if email_content:
        email_text = email_content
    elif file and file.filename != '':
        file_extension = file.filename.split('.')[-1].lower()

        try:
            content = await file.read()

            if file_extension == 'txt':
                email_text = content.decode('utf-8')

            elif file_extension == 'pdf':
                email_text = ""
                pdf_file = io.BytesIO(content)
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    email_text += page.extract_text() + "\n"
            else:
                raise HTTPException(status_code=400, detail="Formato de arquivo não suportado. Use .txt ou .pdf.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao ler/processar o arquivo: {e}")
    
    if not email_text:
        raise HTTPException(status_code=400, detail="Nenhum conteúdo de email ou arquivo fornecido para processamento.")
    
    resultado = process_email_with_ai(email_text)
    return resultado