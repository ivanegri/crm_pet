# Pet Shop CRM

Este é um sistema de CRM para Pet Shops construído com Flask.

## Como rodar localmente

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute a aplicação:
   ```bash
   python3 app.py
   ```
3. Acesse `http://localhost:5000`

## Como fazer o deploy (Servidor Externo)

### Opção 1: Docker (Recomendado)

1. Construa a imagem Docker:
   ```bash
   docker build -t crm-pet .
   ```
2. Rode o container:
   ```bash
   docker run -p 5000:5000 crm-pet
   ```

### Opção 2: Servidor Linux (Ubuntu/Debian)

1. Atualize o servidor e instale Python/Pip:
   ```bash
   sudo apt update && sudo apt install python3-pip python3-venv
   ```
2. Clone este repositório ou copie os arquivos para o servidor.
3. Crie um ambiente virtual e instale as dependências:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Rode com Gunicorn (Servidor de Produção):
   ```bash
   gunicorn -w 4 -b 0.0.0.0:80 app:app
   ```
   *(Nota: Para rodar na porta 80, pode ser necessário sudo ou configurar um proxy reverso como Nginx)*
