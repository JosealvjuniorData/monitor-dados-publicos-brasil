# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 11:17:24 2026

@author: josej
"""
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import json
import os
import sys
import base64
import streamlit.components.v1 as components 
import numpy as np 
from google.cloud import bigquery
from google.oauth2 import service_account

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Monitor de Dados Públicos", page_icon="📊")

# --- 💉 VACINA ANTI-ERRO NUMPY ---
if not hasattr(np, 'VisibleDeprecationWarning'):
    np.VisibleDeprecationWarning = UserWarning

# --- IMPORTAÇÃO BLINDADA (PyGWalker & Sweetviz) ---
try:
    import pygwalker as pyg
    from pygwalker.api.streamlit import StreamlitRenderer
    TEM_PYGWALKER = True
except ImportError:
    TEM_PYGWALKER = False

try:
    # Tenta importar pkg_resources para compatibilidade com Sweetviz
    import pkg_resources 
    import sweetviz as sv
    TEM_SWEETVIZ = True
    ERRO_SWEETVIZ = None
except ImportError:
    try:
        # Tentativa secundária forçando setuptools
        import setuptools
        import pkg_resources
        import sweetviz as sv
        TEM_SWEETVIZ = True
        ERRO_SWEETVIZ = None
    except Exception as e:
        TEM_SWEETVIZ = False
        ERRO_SWEETVIZ = str(e)
except Exception as e:
    TEM_SWEETVIZ = False
    ERRO_SWEETVIZ = str(e)

# --- FUNÇÃO MÁGICA: LINK PARA NOVA ABA ---
def criar_link_nova_aba(html_content, titulo_botao, nome_arquivo):
    """
    Empacota o HTML inteiro dentro de um link para abrir em nova aba.
    Isso simula o comportamento 'show()' local na nuvem.
    """
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'''
    <a href="data:text/html;base64,{b64}" download="{nome_arquivo}" target="_blank" 
       style="
       display: inline-block;
       text-decoration: none;
       background-color: #4CAF50;
       color: white;
       padding: 12px 24px;
       border-radius: 8px;
       font-weight: bold;
       font-size: 16px;
       border: 1px solid #45a049;
       box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
       transition: 0.3s;
       margin-bottom: 20px;
       ">
       🔗 {titulo_botao} <br>
       <span style="font-size:12px; font-weight:normal;">(Clique para abrir em nova janela)</span>
    </a>
    '''
    return href

# --- AUTENTICAÇÃO ---
try:
    if "gcp_service_account" not in st.secrets:
        st.error("❌ Segredos não encontrados.")
        st.stop()
    info_credenciais = dict(st.secrets["gcp_service_account"])
    credenciais = service_account.Credentials.from_service_account_info(info_credenciais)
    project_id = info_credenciais.get("project_id")
except Exception as e:
    st.error(f"❌ Erro na Autenticação: {e}")
    st.stop()

# --- CARREGAR CATÁLOGO ---
ARQUIVO_CATALOGO = "catalogo_mvp.json"
def carregar_catalogo():
    if os.path.exists(ARQUIVO_CATALOGO):
        with open(ARQUIVO_CATALOGO, "r", encoding="utf-8") as f:
            return json.load(f)
    return None
catalogo_atual = carregar_catalogo()

# --- BARRA LATERAL ---
st.sidebar.title("⚙️ Configurações")
st.sidebar.caption(f"🐍 Python: {sys.version.split()[0]}") 

if not catalogo_atual:
    st.sidebar.warning("⚠️ Catálogo vazio.")
    catalogo_atual = {} 

st.sidebar.subheader("🔍 Explorador")
tema = st.sidebar.selectbox("1. Tema:", list(catalogo_atual.keys()), index=None)
orgao, tabela_nome, tabela_id = None, None, None

if tema:
    orgao = st.sidebar.selectbox("2. Dataset:", list(catalogo_atual[tema].keys()), index=None)
    if orgao:
        tabela_nome = st.sidebar.selectbox("3. Tabela:", list(catalogo_atual[tema][orgao].keys()), index=None)
        if tabela_nome:
            tabela_id = catalogo_atual[tema][orgao][tabela_nome]

st.sidebar.divider()
st.sidebar.subheader("🎯 Filtros")
agrupar_brasil = st.sidebar.checkbox("🧮 Visão Nacional (Agregada)", value=False)
ano_minimo = st.sidebar.number_input("Ano inicial:", min_value=1990, max_value=2026, value=2018)

if not agrupar_brasil:
    filtrar_uf = st.sidebar.checkbox("Filtrar por UF?", value=True)
    sigla_uf = st.sidebar.selectbox("UF:", ["DF", "SP", "RJ", "MG", "BA", "RS", "PR", "PE", "SC", "GO"], index=0) if filtrar_uf else None
else:
    sigla_uf = None

# --- EXTRAÇÃO INTELIGENTE (SEM ERROS DE COLUNA) ---
@st.cache_data(ttl=3600)
def extrair_dados(tabela_sql, proj_id, ano_min=None, uf=None, agrupar=False):
    tabela_full = f"basedosdados.{tabela_sql}" if not tabela_sql.startswith("basedosdados.") else tabela_sql
    client = bigquery.Client(credentials=credenciais, project=proj_id, location="US")
    
    # 1. Espião de colunas: Verifica o que existe antes de filtrar
    try:
        table_ref = client.get_table(tabela_full)
        colunas_existentes = [c.name for c in table_ref.schema]
    except:
        colunas_existentes = []

    # 2. Lógica Específica (Frota/Caged)
    if agrupar and ("frota" in tabela_sql or "caged" in tabela_sql):
        query = f"""
        SELECT ano, mes, tipo_veiculo, SUM(quantidade) as quantidade 
        FROM `{tabela_full}`
        WHERE ano >= {ano_min}
        GROUP BY ano, mes, tipo_veiculo
        ORDER BY ano DESC, mes DESC
        LIMIT 2000
        """
    else:
        # 3. Lógica Genérica Inteligente
        query = f"SELECT * FROM `{tabela_full}` WHERE 1=1"
        
        # Só aplica filtro se a coluna existir
        if ano_min and 'ano' in colunas_existentes: 
            query += f" AND ano >= {ano_min}"
        
        if uf and 'sigla_uf' in colunas_existentes: 
            query += f" AND sigla_uf = '{uf}'"
            
        # Ordenação automática se possível
        if 'ano' in colunas_existentes and 'mes' in colunas_existentes:
            query += " ORDER BY ano DESC, mes DESC"
        elif 'ano' in colunas_existentes:
            query += " ORDER BY ano DESC"

        query += " LIMIT 5000" 
    
    try:
        job = client.query(query)
        # Importante: create_bqstorage_client=False evita travamento na nuvem
        df = job.to_dataframe(create_bqstorage_client=False)
        return df
    except Exception as e:
        raise Exception(f"Erro SQL: {e}")

# --- ÁREA PRINCIPAL ---
st.title("📚 Monitor de Dados Públicos")

if tabela_id:
    st.write(f"### 📂 Base: **{tabela_nome}**")
    
    if st.button("🚀 Carregar Dados", type="primary"):
        with st.spinner("Baixando dados do Google BigQuery..."):
            try:
                df = extrair_dados(tabela_id, project_id, ano_minimo, sigla_uf, agrupar_brasil)
                
                # Tratamento de Data para Gráficos
                if 'ano' in df.columns and 'mes' in df.columns:
                    try:
                        df['data_referencia'] = pd.to_datetime(df['ano'].astype(str) + '-' + df['mes'].astype(str) + '-01', errors='coerce')
                        df = df.sort_values('data_referencia')
                    except: pass
                
                st.session_state['df_analise'] = df
                st.success(f"Sucesso! {len(df)} linhas carregadas.")
            except Exception as e:
                st.error(f"Erro ao carregar: {e}")
                
    if 'df_analise' in st.session_state:
        df = st.session_state['df_analise']
        
        st.divider()
        opcoes_nav = ["📄 Dados Brutos"]
        if TEM_PYGWALKER: opcoes_nav.append("🎨 BI Self-Service")
        if TEM_SWEETVIZ: opcoes_nav.append("🍭 Relatório Automático")
            
        escolha = st.radio("Escolha a Visualização:", opcoes_nav, horizontal=True)
        st.divider()
        
        if escolha == "📄 Dados Brutos":
            st.dataframe(df, use_container_width=True)
            
        elif escolha == "🎨 BI Self-Service":
            if TEM_PYGWALKER:
                try:
                    st.info("💡 Clique no botão abaixo para uma experiência de tela cheia (igual Desktop).")
                    
                    # 1. BOTÃO VERDE DE "NOVA ABA"
                    # Gera o HTML completo do PyGWalker para download/abertura
                    html_pyg = pyg.to_html(df)
                    st.markdown(criar_link_nova_aba(html_pyg, "Abrir BI em Tela Cheia", "bi_analise.html"), unsafe_allow_html=True)
                    
                    st.write("---")
                    st.write("**Ou use a versão embarcada abaixo:**")

                    # 2. VERSÃO EMBARCADA
                    df_safe = df.copy()
                    for col in df_safe.columns:
                        if df_safe[col].dtype == 'object':
                            df_safe[col] = df_safe[col].astype(str)
                    
                    # StreamlitRenderer é essencial para não dar tela branca
                    renderer = StreamlitRenderer(df_safe, spec="./gw_config.json", spec_io_mode="RW")
                    renderer.explorer()
                    
                except Exception as e:
                    st.error(f"Erro PyGWalker: {e}")

        elif escolha == "🍭 Relatório Automático":
             if TEM_SWEETVIZ:
                if st.button("Gerar Relatório (IA)"):
                    with st.spinner("A Inteligência Artificial está analisando os dados..."):
                        # Analisa
                        analise = sv.analyze(df)
                        analise.show_html("relatorio.html", open_browser=False)
                        
                        # Lê o arquivo gerado
                        with open("relatorio.html", 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        st.success("Relatório pronto!")
                        
                        # 1. BOTÃO VERDE DE "NOVA ABA"
                        st.markdown(criar_link_nova_aba(html_content, "Abrir Relatório Completo", "relatorio_ia.html"), unsafe_allow_html=True)
                        
                        st.write("---")
                        st.write("**Prévia do Relatório:**")
                        
                        # 2. VERSÃO EMBARCADA
                        components.html(html_content, height=800, scrolling=True)

else:
    st.info("👈 Selecione uma base no menu lateral para começar.")