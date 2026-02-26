# 📊 Monitor de Dados Públicos Brasileiros

> **Uma aplicação Full-Stack de Business Intelligence para análise de dados governamentais em tempo real.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://monitor-dados-publicos-brasil-khrxgz3wbepovacjuqzu5u.streamlit.app/)
👆 **Clique no botão acima para acessar o Painel Online!**

---

## 🎯 Sobre o Projeto

O grande objetivo desta ferramenta é permitir que qualquer pessoa possa entender minimamente uma base de dados sem a necessidade de baixar arquivos gigantescos ou realizar todo o processo manual de análise exploratória.

Muitas vezes, perde-se muito tempo preparando um ambiente local apenas para descobrir que a base não possui os dados necessários para o seu problema. Este painel serve como um laboratório rápido: você visualiza, explora e valida a qualidade da informação antes de decidir se vale a pena utilizá-la em trabalhos maiores.

Desenvolvi esse projeto para democratizar o acesso a grandes volumes de dados públicos (Big Data), permitindo que qualquer cidadão analise tendências históricas sem precisar saber programar em SQL ou Python.

A aplicação conecta diretamente ao *Data Lakehouse* da [**Base dos Dados**](https://basedosdados.org/)
 (BigQuery), processa milhões de linhas e gera visualizações interativas e relatórios estatísticos automáticos.



### 🛠️ Tecnologias e Ferramentas

* **Linguagem:** Python 3.11
* **Engenharia de Dados:** Google BigQuery (SQL), Pandas, `basedosdados`
* **Frontend & UX:** Streamlit
* **Analytics:** Plotly (Gráficos), PyGWalker (Self-Service BI tipo Tableau)
* **Data Science:** Sweetviz (EDA e Relatórios Estatísticos com IA)

---

### 🚀 Desafios Superados (A Jornada Técnica)

Para chegar a este produto estável, superamos diversos desafios de infraestrutura e engenharia de dados que surgiram durante o desenvolvimento:

Sanitização "Nuclear" de Dados: Implementamos um extrator que limpa tipos de dados exóticos (como o dbdate do BigQuery) que costumam travar bibliotecas de visualização como o PyGWalker.

Extração Defensiva: O motor de busca escaneia a tabela no Google Cloud antes da query, evitando erros de "coluna não encontrada" (como o erro de ano ou sigla_uf) em bases heterogêneas.

Compatibilidade de Ambiente: Configuramos um ambiente híbrido (Python 3.11 + setuptools<70) para permitir que bibliotecas de análise modernas e ferramentas clássicas de IA rodem em harmonia na nuvem.

UX Desktop-to-Web: Desenvolvemos um sistema de links em Base64 que permite abrir relatórios pesados em abas independentes, simulando a experiência de um software instalado no computador.

---

## 🚀 Funcionalidades Principais

1.  **Explorador de Dados:** Navegação por temas (Economia, Segurança, Meio Ambiente, etc.).
2.  **Motor de Busca SQL:** Filtros dinâmicos que rodam diretamente na nuvem antes de baixar o dado.
3.  **Agregação Inteligente:** Capacidade de visualizar dados granulares (por município) ou agregados (Brasil todo).
4.  **Self-Service BI:** O usuário cria seus próprios gráficos arrastando e soltando colunas (Drag & Drop).
5.  **Relatórios IA:** Geração automática de HTML com correlações, distribuição e análise de dados.

---
## 📖 Como Expandir o Catálogo (Guia Prático)

O projeto foi desenhado para ser modular. Para adicionar um novo Tema, Dataset ou Tabela, você não precisa mexer no código Python, basta editar o arquivo catalogo_mvp.json.

Onde encontrar o ID Técnico?
Acesse a [Pesquida da base dos dados][https://basedosdados.org/search]

Pesquise pelo tema desejado e clique no conjunto de dados (Dataset).

No menu lateral esquerdo, você encontrará a lista de tabelas disponíveis para aquele dataset.

Clique na tabela desejada e copie o campo "ID da Tabela" que aparecerá no centro da tela (ex: br_ms_sim.microdados).

Passo a Passo da Atualização:
Abra o arquivo catalogo_mvp.json no seu repositório.

Insira a nova entrada seguindo a hierarquia (Tema > Dataset > Tabela).

No valor da Tabela, cole o ID Técnico que você copiou do site.

Faça o git push e a nova base aparecerá instantaneamente no menu do aplicativo!

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
