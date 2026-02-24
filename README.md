# 📊 Monitor de Dados Públicos Brasileiros

> **Uma aplicação Full-Stack de Business Intelligence para análise de dados governamentais em tempo real.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://monitor-dados-publicos-brasil-khrxgz3wbepovacjuqzu5u.streamlit.app/)
👆 **Clique no botão acima para acessar o Painel Online!**

---

## 🎯 Sobre o Projeto

Este projeto foi desenvolvido para democratizar o acesso a grandes volumes de dados públicos (Big Data), permitindo que qualquer cidadão analise tendências históricas sem precisar saber programar em SQL ou Python.

A aplicação conecta diretamente ao *Data Lakehouse* da **Base dos Dados** (BigQuery), processa milhões de linhas e gera visualizações interativas e relatórios estatísticos automáticos.

### 🛠️ Tecnologias e Ferramentas
* **Linguagem:** Python 3.11
* **Engenharia de Dados:** Google BigQuery (SQL), Pandas, `basedosdados`
* **Frontend & UX:** Streamlit
* **Analytics:** Plotly (Gráficos), PyGWalker (Self-Service BI tipo Tableau)
* **Data Science:** Sweetviz (EDA e Relatórios Estatísticos com IA)

---

## 🚀 Funcionalidades Principais

1.  **Explorador de Dados:** Navegação por temas (Economia, Segurança, Meio Ambiente, etc.).
2.  **Motor de Busca SQL:** Filtros dinâmicos que rodam diretamente na nuvem antes de baixar o dado.
3.  **Agregação Inteligente:** Capacidade de visualizar dados granulares (por município) ou agregados (Brasil todo).
4.  **Self-Service BI:** O usuário cria seus próprios gráficos arrastando e soltando colunas (Drag & Drop).
5.  **Relatórios IA:** Geração automática de HTML com correlações, distribuição e análise de dados.

---

## 💻 Como Rodar este Projeto Localmente

Se você é desenvolvedor e quer rodar este código na sua máquina, siga os passos abaixo:

### 1. Pré-requisitos
* Python 3.10 ou superior
* Conta no Google Cloud Platform (para acesso ao BigQuery)

### 2. Instalação
Clone o repositório e instale as dependências:

# Clone o projeto
git clone [https://github.com/JosealvjuniorData/monitor-dados-publicos-brasil.git](https://github.com/JosealvjuniorData/monitor-dados-publicos-brasil.git)

# Entre na pasta
cd monitor-dados-publicos-brasil

# Instale as bibliotecas
pip install -r requirements.txt

### 3. Configuração de Credenciais (Importante! 🔐)
Este projeto exige uma chave de serviço do Google Cloud (BigQuery).

Crie um projeto no Google Cloud Console.

Gere uma chave JSON para uma Service Account.

Renomeie o arquivo para credenciais.json e coloque na raiz do projeto.

Nota: O arquivo credenciais.json está no .gitignore para segurança.

### 4. Execução
Rode o comando do Streamlit:
streamlit run app.py

## 📝 Licença
Este projeto é de código aberto (Open Source). Sinta-se à vontade para contribuir!

Desenvolvido por José Alves Junior

**Pronto!** Agora sim está completo, com o link do seu app funcionando e o seu nome no final. Copie tudo isso e mande ver no GitHub! 🚀
