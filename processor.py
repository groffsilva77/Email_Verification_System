import os
import json
from google import genai
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv

load_dotenv()

try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente GEMINI_API_KEY não foi encontrada.")
    
    client = genai.Client(api_key=api_key)

except Exception as e:
    print(f"Erro ao inicializar o cliente Gemnini: {e}")
    client = None

def process_email_with_ai(email_text: str) -> dict:
    """
    Classifica o email em 'Produtivo' ou 'Improdutivo' e sugere uma resposta
    usando a API da OpenAI.
    """
    if not client:
        return {"categoria": "Erro de Inicialização", "resposta_sugerida": "O cliente Gemini não foi inicializado. Verifique a chave de API."}

    if not email_text:
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
    EMAIL:
    {email_text}
    ---
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

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=json_schema,
            )
        )

        ai_output = response.text
        result_dict = json.loads(ai_output)

        return {
            "categoria": result_dict.get("categoria", "Não Classificado"),
            "resposta_sugerida": result_dict.get("resposta_sugerida", "Não foi possível gerar a resposta.")
        }
    
    except APIError as e:
        print(f"Erro de API do Gemini: {e}")
        return {"categoria": "Erro de API", "resposta_sugerida": f"Ocorreu um erro na comunicação com o Gemini: {e}"}
    except Exception as e:
        print(f"Erro em chamada de processamento: {e}")
        return {"categoria": "Erro de AI", "resposta_sugerida": f"Ocorreu um erro no processamento: {e}"}