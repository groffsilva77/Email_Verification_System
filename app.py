import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pypdf import PdfReader
import io
import logging
from processor import process_email_with_ai

logging.basicConfig(level=logging.INFO, format='%(acstime)s - %(levelname)s - %(message)s')

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
        logging.info(f"Arquivo recebido: {file.filename}, Extensão: {file_extension}")

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

                if len(email_text.strip()) == 0:
                    raise ValueError("O PDF não contém texto legível ou está vazio.")
            else:
                logging.warning(f"Formato de arquivo não suportado: {file_extension}")
                raise HTTPException(status_code=400, detail="Formato de arquivo não suportado. Use .txt ou .pdf.")
        except ValueError as ve:
            logging.error(f"Erro de validação de conteúdo: {ve}")
            raise HTTPException(status_code=400, detail=f"Erro de validação do arquivo; {ve}")
        except Exception as e:
            logging.error(f"Erro ao ler/processar o arquivo {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Erro ao ler/processar o arquivo: {e}")
    
    if not email_text:
        logging.warning("Tentaiva de processamento com texto vazio.")
        raise HTTPException(status_code=400, detail="Nenhum conteúdo de email ou arquivo fornecido para processamento.")
    
    try:
        resultado = process_email_with_ai(email_text)
        
        if resultado.get("Categoria", "").startswith("Erro"):
            logging.error(f"Erro reportado pelo processador: {resultado['resposta_sugerida']}")
            raise HTTPException(status_code=500, detail=resultado['resposta_sugerida'])
        return resultado
    except Exception as e:
        logging.error(f"Falha de processamento de AI: {e}")
        raise HTTPException(status_code=500, detail=f"Falha de processamento de IA:: {e}")

    