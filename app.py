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
import streamlit.components.v1 as components 
import plotly.express as px
import numpy as np 
from google.cloud import bigquery
from google.oauth2 import service_account # Importante para autenticação robusta

# --- 💉 VACINA ANTI-ERRO NUMPY ---
if not hasattr(np, 'VisibleDeprecationWarning'):
    np.VisibleDeprecationWarning = UserWarning

# --- IMPORTAÇÃO BLINDADA ---
try:
    import pygwalker as pyg
    TEM_PYGWALKER = True
except ImportError:
    TEM_PYGWALKER = False

try:
    import sweetviz as sv
    TEM_SWEETVIZ = True
except ImportError:
    TEM_SWEETVIZ = False

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Catálogo BI Público", page_icon="📊")

# --- AUTENTICAÇÃO ROBUSTA (A CORREÇÃO PRINCIPAL) ---
# Em vez de tempfile, vamos criar o arquivo na raiz se ele não existir
if not os.path.exists("credenciais.json"):
    if "gcp_service_account" in st.secrets:
        try:
            with open("credenciais.json", "w") as f:
                json.dump(dict(st.secrets["gcp_service_account"]), f)
        except Exception as e:
            st.error(f"Erro ao criar arquivo de credenciais: {e}")

# Define a variável de ambiente explicitamente
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credenciais.json"

ARQUIVO_CATALOGO = "catalogo_mvp.json"

def carregar_catalogo():
    if os.path.exists(ARQUIVO_CATALOGO):
        with open(ARQUIVO_CATALOGO, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

catalogo_atual = carregar_catalogo()

# --- BARRA LATERAL ---
st.sidebar.title("⚙️ Configurações")
st.sidebar.info(
    "ℹ️ **Fonte de Dados:** Base dos Dados (BigQuery). "
    "Indicadores podem ter atraso devido ao processamento oficial."
)

# SEU ID DO PROJETO GOOGLE CLOUD (Confirme se é este mesmo no console do Google)
project_id = "paineldadosabertos" 

if not catalogo_atual:
    st.sidebar.error("⚠️ Catálogo não encontrado. Verifique se 'catalogo_mvp.json' está no GitHub.")
    st.stop()

st.sidebar.subheader("🔍 Explorador de Bases")
tema = st.sidebar.selectbox("1. Tema:", list(catalogo_atual.keys()), index=None)

orgao, tabela_nome, tabela_id = None, None, None

if tema:
    orgao = st.sidebar.selectbox("2. Dataset:", list(catalogo_atual[tema].keys()), index=None)
    if orgao:
        tabela_nome = st.sidebar.selectbox("3. Tabela:", list(catalogo_atual[tema][orgao].keys()), index=None)
        if tabela_nome:
            tabela_id = catalogo_atual[tema][orgao][tabela_nome]

st.sidebar.divider()
st.sidebar.subheader("🎯 Estratégia de Dados")

agrupar_brasil = st.sidebar.checkbox("🧮 Visão Nacional Agregada", value=False)

st.sidebar.subheader("🌪️ Filtros")
ano_minimo = st.sidebar.number_input("Ano inicial:", min_value=1990, max_value=2026, value=2018)

if not agrupar_brasil:
    filtrar_uf = st.sidebar.checkbox("Filtrar por UF?")
    sigla_uf = st.sidebar.selectbox("UF:", ["DF", "SP", "RJ", "MG", "BA", "RS", "PR", "PE"], index=0) if filtrar_uf else None
else:
    sigla_uf = None
    st.sidebar.caption("🚫 Filtro de UF desativado no modo Agregado.")

# --- EXTRAÇÃO DE DADOS OTIMIZADA ---

@st.cache_data(ttl=3600)
def extrair_dados(tabela_sql, proj_id, ano_min=None, uf=None, agrupar=False):
    # Ajusta o nome da tabela
    tabela_full = f"basedosdados.{tabela_sql}" if not tabela_sql.startswith("basedosdados.") else tabela_sql
    
    # --- QUERY ---
    if agrupar and ("frota" in tabela_sql or "caged" in tabela_sql):
        query = f"""
        SELECT ano, mes, tipo_veiculo, SUM(quantidade) as quantidade 
        FROM `{tabela_full}`
        WHERE ano >= {ano_min}
        GROUP BY ano, mes, tipo_veiculo
        ORDER BY ano DESC, mes DESC
        LIMIT 1000
        """
    else:
        query = f"SELECT * FROM `{tabela_full}` WHERE 1=1"
        if ano_min: query += f" AND ano >= {ano_min}"
        if uf: query += f" AND sigla_uf = '{uf}'"
        
        # REMOVI O ORDER BY PESADO TEMPORARIAMENTE PARA TESTE
        # query += " ORDER BY ano DESC" 
        
        # --- LIMITE DE SEGURANÇA (IMPORTANTE) ---
        # Reduzido para 100 apenas para destravar o app. Se funcionar, aumentamos.
        query += " LIMIT 100" 
    
    # --- CONEXÃO ---
    try:
        # Forçamos o cliente a usar o projeto correto e as credenciais do arquivo
        client = bigquery.Client(project=proj_id)
        job = client.query(query)
        df = job.to_dataframe()
        return df
    except Exception as e:
        raise Exception(f"Erro no BigQuery: {e}")

# --- ÁREA PRINCIPAL ---
st.title("📚 Catálogo Analítico de Dados Públicos")

if tabela_id:
    st.write(f"### Analisando: **{tabela_nome}**")
    st.caption(f"ID da Tabela: `{tabela_id}`")
    
    if st.button("🚀 Carregar e Analisar Dados", type="primary"):
        with st.spinner("Conectando ao Google BigQuery..."):
            try:
                df = extrair_dados(tabela_id, project_id, ano_minimo, sigla_uf, agrupar_brasil)
                
                # Tratamento de Data
                if 'ano' in df.columns and 'mes' in df.columns:
                    try:
                        df['data_referencia'] = pd.to_datetime(
                            df['ano'].astype(str) + '-' + df['mes'].astype(str) + '-01',
                            errors='coerce'
                        )
                        df = df.sort_values('data_referencia')
                    except: pass

                st.session_state['df_analise'] = df
                st.success("Dados carregados com sucesso!") # Feedback visual
            except Exception as e:
                st.error(f"Falha na extração: {e}")
                
    if 'df_analise' in st.session_state:
        df = st.session_state['df_analise']
        
        st.divider()
        opcoes_nav = ["📄 Dados Brutos"]
        if TEM_PYGWALKER: opcoes_nav.append("🎨 BI Self-Service")
        if TEM_SWEETVIZ: opcoes_nav.append("🍭 Relatório IA")
            
        escolha = st.radio("Escolha a Visualização:", opcoes_nav, horizontal=True)
        st.divider()
        
        if escolha == "📄 Dados Brutos":
            st.dataframe(df, use_container_width=True)
            
        elif escolha == "🎨 BI Self-Service":
            if TEM_PYGWALKER:
                try:
                    df_safe = df.copy()
                    # Converte tudo que é objeto para string para evitar erro do PyGWalker
                    for col in df_safe.columns:
                        if df_safe[col].dtype == 'object':
                            df_safe[col] = df_safe[col].astype(str)
                    
                    pyg_html = pyg.walk(df_safe, return_html=True)
                    components.html(pyg_html, height=1000, scrolling=True)
                except Exception as e:
                    st.error(f"Erro PyGWalker: {e}")

        elif escolha == "🍭 Relatório IA":
             if TEM_SWEETVIZ:
                if st.button("Gerar Relatório"):
                    analise = sv.analyze(df)
                    analise.show_html("relatorio.html", open_browser=False)
                    with open("relatorio.html", 'r', encoding='utf-8') as f:
                        components.html(f.read(), height=1000, scrolling=True)

else:
    st.info("👈 Selecione uma base no menu lateral.")