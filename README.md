# MovieSearch: Sistema de Recomendação de Filmes com Grafos
Este é um projeto full-stack que utiliza um grafo de conhecimento e o algoritmo A* para fornecer recomendações inteligentes de filmes.

## 🚀 Arquitetura
O sistema é dividido em três componentes principais que precisam de ser executados em paralelo:

1. Frontend: Uma interface de utilizador moderna e reativa construída com React, TypeScript e estilizada com Tailwind CSS.
2. Backend: Uma API robusta e de alta performance construída com Python e FastAPI, responsável por toda a lógica de negócio.
3. Banco de Dados: Um banco de dados de grafos Neo4j para armazenar e consultar as conexões entre filmes, diretores e géneros.
4. Fonte de Dados Externa: A API do The Movie Database (TMDB) para popular o grafo com informações reais dos filmes.

## 📋 Pré-requisitos
Antes de começar, certifique-se de que tem o seguinte software instalado na sua máquina:

* Node.js (versão 18 ou superior)
* Python (versão 3.10 ou superior)
* Neo4j Desktop

## ⚙️ Configuração Inicial
1. Clone o Repositório:

  git clone https://github.com/M00NCX/aed2-movies

2. Configure as Variáveis de Ambiente:
  A comunicação entre o backend, o TMDB e o Neo4j depende de chaves e senhas secretas.
  * Navegue até à pasta do backend (/movies).
  * Crie um ficheiro chamado .env.
  * Copie e cole o conteúdo abaixo no ficheiro .env, substituindo os valores pelos seus:

    **Chave da API obtida no site The Movie Database (TMDB)**
    
    TMDB_API_KEY="a_sua_chave_secreta_aqui"
    
    **Credenciais do seu banco de dados Neo4j local**
    
    NEO4J_URI="neo4j://localhost:7687"
    NEO4J_USER="neo4j"
    NEO4J_PASSWORD="a_sua_senha_do_neo4j"

## ▶️ Como Executar a Aplicação
Para que a aplicação funcione, os três serviços (Banco de Dados, Backend e Frontend) precisam de estar a correr ao mesmo tempo. Recomendo abrir três terminais separados.

### **Terminal 1: Iniciar o Banco de Dados (Neo4j)**
1. Abra o aplicativo Neo4j Desktop.
2. Encontre o seu banco de dados na lista de projetos.
3. Clique no botão "Start".
4. Aguarde até o status mudar para ativo (bolinha verde). Mantenha o Neo4j Desktop aberto.

### **Terminal 2: Iniciar o Backend (FastAPI)**
1. Navegue até à pasta do seu projeto backend.
       cd movies

2. Crie e ative um ambiente virtual Python (recomendado):

    Criar ambiente
     python -m venv venv
    Ativar ambiente (Windows)
     .\venv\Scripts\activate
    Ativar ambiente (macOS/Linux)
     source venv/bin/activate

3. Instale as dependências Python:

    pip install -r requirements.txt

4. Inicie o servidor FastAPI com o Uvicorn:

    uvicorn src.main:app --reload

5. Você deverá ver uma mensagem a dizer Uvicorn running on http://127.0.0.1:8000. Deixe este terminal a correr.

### **Terminal 3: Iniciar o Frontend (React)**
1. Navegue até à pasta do seu projeto frontend (que provavelmente está dentro da pasta do backend).

    Exemplo, ajuste o caminho se necessário
    cd movies 

2. Instale as dependências do Node.js:

    npm install

3. Inicie o servidor de desenvolvimento do Vite:

    npm run dev

4. O terminal mostrará uma URL local. Abra o seu navegador e aceda a http://localhost:5173 (ou a porta que for indicada).

Agora, a sua aplicação completa está a funcionar! Você pode pesquisar por um filme e ver a magia acontecer.
