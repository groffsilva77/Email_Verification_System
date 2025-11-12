import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def process_email_with_ai(email_text: str) -> dict:
    """
    Classifica o email em 'Produtivo' ou 'Improdutivo' e sugere uma resposta
    usando a API da OpenAI.
    """
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

    Retorne a resposta EXCLUSIVAMENTE no formato JSON, sem nenhum texto adicional.
    JSON SCHEMA: {{"categoria": "CLASSIFICAÇÃO", "resposta_sugerida": "TEXTO DA RESPOSTA"}}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente de triagem de email que retorna a saída em JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        ai_output = response.choices[0].message.content
        result_dict = json.loads(ai_output)

        return {
            "categoria": result_dict.get("categoria", "Não Classificado"),
            "resposta_sugerida": result_dict.get("resposta_sugerida", "Não foi possível gerar a resposta.")
        }
    
    except Exception as e:
        print(f"Erro em chamada à API: {e}")
        return {"categoria": "Erro de AI", "resposta_sugerida": f"Ocorreu um erro no processamento: {e}"}