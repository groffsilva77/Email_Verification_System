📧 AutoClassificador de Emails Financeiros

O AutoClassificador de Emails Financeiros é uma aplicação web Full-Stack construída com FastAPI (Python) e Gemini API (Google AI) que atua como um assistente de triagem inteligente.

Ele analisa o conteúdo de emails ou documentos de texto/PDFs, classifica-os como 'Produtivo' (requer ação) ou 'Improdutivo' (social, agradecimento), e gera automaticamente uma resposta concisa e profissional baseada na categoria.

---

🚀 Funcionalidades Principais
Classificação Inteligente: Utiliza o modelo Gemini com engenharia de prompt Few-Shot para categorizar emails em 'Produtivo' ou 'Improdutivo' com alta precisão.

Geração Automática de Resposta: Sugere respostas personalizadas de acordo com a classificação do email.

Suporte a Múltiplos Formatos: Aceita entrada de texto via formulário ou upload de arquivos .txt e .pdf.

Arquitetura Robusta: O backend possui lógica de logging, validação de esquema JSON e retentativas (retry com exponential backoff) para garantir resiliência contra falhas transientes da API.

Design Moderno: Interface de usuário construída com HTML, CSS e Tailwind CSS, com uma paleta de cores predominante em laranja (tema financeiro).

🛠️ Tecnologias Utilizadas

Backend API -----------> Python, FastAPI
Inteligência Artificial -----------> Gemini API (Google AI)
Leitura de PDF -----------> pypdf
Frontend -----------> HTML, JavaScript, Tailwind CSS
Gerenciamento de Ambiente -----------> pip, .env

⚙️ Como Rodar Localmente

Siga os passos abaixo para configurar e rodar a aplicação em sua máquina:

1. Pré-requisitos
   Certifique-se de ter o Python (3.8+) e o pip instalados.
2. Configuração do Ambiente
   1. Clone o repositório do projeto.
   2. Crie um ambiente virtual e ative-o:
      python -m venv venv
      source venv/bin/activate # No Linux/macOS
      .\venv\Scripts\activate # No Windows
   3. Instale as dependências
      pip install -r requirements.txt
3. Configurações da Chave de API
   1. Crie um arquivo chamado .env na raiz do projeto
   2. Obtenha sua chave de API no Google AI Studio
   3. Adicione a chave ao arquivo .env no formato:
      GEMINI_API_KEY="SUA_CHAVE_AQUI"
4. Inicialização do Servidor
   Execute o servidor Uvicorn a partir da raiz do projeto:
   uvicorn app:app --reload
   Obs.: ele estará acessível em: http://127.0.0.1:8000, abra ele em uma guia anônima

Deploy

O projeto está configurado para um deploy fácil em serviços de hospedagem de aplicações web Python, como Render ou Heroku.

1. Certifique-se de que requirements.txt e Procfile estão atualizados.
2. Defina a variável de ambiente GEMINI_API_KEY diretamente na plataforma de hospedagem (NUNCA a envie via Git).
3. Use o comando uvicorn app:app --host 0.0.0.0 --port $PORT como comando de inicalização.
