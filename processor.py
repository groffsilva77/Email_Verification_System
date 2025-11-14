import os
import json
import time
import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

client = None
MAX_RETRIES = 3
INITIAL_DELAY = 1

def initialize_gemini_client():
    """Inicializa o cliente Gemini de forma robusta e global."""
    global client
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logging.error("A variável de ambiente GEMINI_API_KEY não foi encontrada.")
            raise ValueError("Chave de API do Gemini ausente.")
    
        client = genai.Client(api_key=api_key)
        logging.info("Cliente Gemini inicializado com sucesso.")

    except Exception as e:
        logging.critical(f"Erro CRÍTICO ao inicializar o cliente Gemini: {e}")
        client = None

initialize_gemini_client()

def process_email_with_ai(email_text: str) -> dict:
    """
    Classifica o email em 'Produtivo' ou 'Improdutivo' e sugere uma resposta
    usando a API da OpenAI.
    """
    if not client:
        return {"categoria": "Erro de Inicialização", "resposta_sugerida": "O cliente Gemini não foi inicializado. Verifique a chave de API."}

    if not email_text:
        logging.warning("Texto do email vazio recebido para processamento.")
        return {"categoria": "Erro", "resposta_sugerida": "O texto do email está vazio."}
    
    prompt = f"""
    Você é um assistente de triagem de emails para um grande setor financeiro.
    Sua tarefa é analisar o EMAIL abaixo e classificá-lo estritamente em uma das duas categorias:
    'Produtivo' (requer ação, suporte técnico, ou atualização de caso) ou
    'Improdutivo' (agradecimento, felicitações, mensagem social ou pergunta não relevante).

    Após classificar, gere uma 'Resposta Sugerida' concisa e profissional baseada na categoria:
    - Se 'Produtivo': A resposta deve confirmar o recebimento e informar que a solicitação
      está sendo processada e será tratada pela equipe.
    - Se 'Improdutivo': A resposta deve ser um agradecimento cordial e encerrar a conversa.

    ---
    EXEMPLOS DE CLASSIFICAÇÃO PARA REFERÊNCIA:
    # Exemplo 1 (Produtivo - Suporte Técnico)
    EMAIL: O acesso ao nosso sistema da negociação parou de funcionar após a autalização de hoje. Minha ID é 456.
    SAÍDA ESPERADA: {{"categoria": "Produtivo", "resposta_sugerida": "Prezado(a), confirmamos o recebimento da sua solicitação de suporte. O incidente com a ID 456 está sendo analisado pela nossa equipe técnica e você receberá uma atualização em breve."}}
    
    # Exemplo 2 (Improdutivo - Social/Agradecimento)
    EMAIL: Só queria agradecer a você e à sua equipe pelo excelente suporte que recebemos na semana passada. Ótimo trabalho!
    SAÍDA ESPERADA: {{"categoria": "Improdutivo", "resposta_sugerida": "Prezado(a), ficamos muito felizes em saber que o suporte foi satisfatório. Agradecemos o feedback e estamos sempre à disposição!"}}

    # Exemplo 3 (Produtivo - Requer Ação/Documentação)
    EMAIL: Em anexo, estou enviando o formulário de KYC atualizado que vocês solicitaram na última reunião. Por favor, confirmem o recebimento.
    SAÍDA ESPERADA: {{"categoria": "Produtivo", "resposta_sugerida": "Prezado(a), o documento de kYC foi recebido. Nossa equipe de conformidade irá processar a atualização nos próximos passos. Agradecemos o envio."}}

    # Exemplo 4 (Improdutivo - Não acionável)
    EMAIL: Olá, vocês acham que o mercado de ações vai subir na próxima semana?
    SAÍDA ESPERADA: {{"categoria": "Improdutivo", "resposta_sugerida": "Prezado(a), agradeçemos o contato. Não fornecemos aconselhamento sobre o mercado futuro. Para informações oficiais, consulte nossos relatórtios regulares."}}
    ---

    ANALISE ESTE EMAIL (USUÁRIO):
    EMAIL:
    {email_text}
    ---
    GERE APENAS O OBJETO JSON FINAL:
    """

    json_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "categoria": types.Schema(
                type=types.Type.STRING,
                description="Classificação: 'Produtivo' ou 'Improdutivo'."
            ),
            "resposta_sugerida": types.Schema(
                type=types.Type.STRING,
                description="A resposta concisa e profissional baseada na classificação."
            )
        },
        required=["categoria", "resposta_sugerida"]
    )

    delay = INITIAL_DELAY
    for attempt in range(MAX_RETRIES):
        try:
            config = types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=json_schema,
            )

            logging.info(f"Tentativa (attempt + 1)/{MAX_RETRIES} de chamar a API Gemini.")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                config=config
            )

            ai_output = response.text
            result_dict = json.loads(ai_output)

            categoria = result_dict.get("categoria")
            resposta = result_dict.get("resposta_sugerida")

            if not categoria or not resposta:
                logging.warning(f"Saída JSON da IA incompleta: {ai_output}")
                raise ValueError("Saída da IA inválida ou incompleta.")
            
            logging.info(f"Processamento bem-sucedido. Categoria: {categoria}")
            return {
                "categoria": categoria,
                "resposta_sugerida": resposta
            }
    
        except APIError as e:
            logging.error(f"Erro de API do Gemini na tentativa {attempt + 1}: {e}")
            if attempt < MAX_RETRIES - 1:
                logging.info(f"Tentando novamente em {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                logging.error("Falha final após todas as retentativas.")
                raise Exception(f"Falha de comunicação com a API Gemini após {MAX_RETRIES} tentativas.") from e
            
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Erro de validação ou parsing JSON na tentativa {attempt + 1}: {e}")
            if attempt < MAX_RETRIES - 1:
                logging.info(f"Tentando novamente em {delay}s (Saída Inválida)...")
                time.sleep(delay)
                delay *= 2
            else:
                logging.error("Falha final devido à saída inválida.")
                raise Exception("A IA gerou uma saída inválida consistentemente.") from e
            
        except Exception as e:
            logging.error(f"Erro inesperado no processamento: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(delay)
                delay *= 2
            else:
                raise Exception(f"Erro inesperado durante o processamento: {e}") from e
    return {"categoria": "Erro de AI", "resposta_sugerida": f"Ocorreu um erro no processamento: {e}"}