# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 11:17:24 2026

@author: josej
"""
import streamlit as st
import basedosdados as bd
import pandas as pd
import json
import os
import streamlit.components.v1 as components 
import plotly.express as px
import numpy as np 

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

# --- AUTENTICAÇÃO INTELIGENTE (LOCAL vs NUVEM) ---
import tempfile

# Se o arquivo local existir, usa ele (Seu computador)
if os.path.exists("credenciais.json"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credenciais.json"
else:
    # Se não existir, estamos na Nuvem!
    # Criamos um arquivo temporário com as senhas que estão nos "Secrets"
    # O basedosdados EXIGE um arquivo físico, então criamos um falso aqui.
    try:
        if "gcp_service_account" in st.secrets:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp:
                json.dump(dict(st.secrets["gcp_service_account"]), temp)
                temp.flush() # Garante que escreveu tudo
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp.name
    except Exception as e:
        st.error(f"Erro de autenticação na nuvem: {e}")

st.set_page_config(layout="wide", page_title="Catálogo BI Público", page_icon="📊")

ARQUIVO_CATALOGO = "catalogo_mvp.json"

def carregar_catalogo():
    if os.path.exists(ARQUIVO_CATALOGO):
        with open(ARQUIVO_CATALOGO, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

catalogo_atual = carregar_catalogo()

# --- BARRA LATERAL ---
st.sidebar.title("⚙️ Configurações")
# --- AVISO DE TRANSPARÊNCIA (NOVO) ---
st.sidebar.info(
    "ℹ️ **Fonte de Dados:** Este painel utiliza a camada gratuita da 'Base dos Dados'. "
    "Alguns indicadores podem apresentar atraso de 3 a 12 meses em relação à data atual "
    "devido às políticas de acesso da API."
)
project_id = "paineldadosabertos" 

if not catalogo_atual:
    st.sidebar.error("⚠️ Catálogo não encontrado. Rode o 'sync_catalogo.py' primeiro.")
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

# NOVA OPÇÃO: Agrupar dados
agrupar_brasil = st.sidebar.checkbox("🧮 Visão Nacional Agregada", value=False, help="Marca essa opção para somar os dados de todos os municípios e ver o histórico completo do Brasil.")

st.sidebar.subheader("🌪️ Filtros")
ano_minimo = st.sidebar.number_input("Ano inicial:", min_value=1990, max_value=2026, value=2018)

# O filtro de UF só faz sentido se NÃO estivermos vendo o agregado nacional
if not agrupar_brasil:
    filtrar_uf = st.sidebar.checkbox("Filtrar por UF?")
    sigla_uf = st.sidebar.selectbox("UF:", ["DF", "SP", "RJ", "MG", "BA", "RS", "PR", "PE"], index=0) if filtrar_uf else None
else:
    sigla_uf = None
    st.sidebar.caption("🚫 Filtro de UF desativado no modo Agregado.")

# --- EXTRAÇÃO DE DADOS (CÉREBRO NOVO) ---
@st.cache_data(ttl=3600)
def extrair_dados(tabela_sql, proj_id, ano_min=None, uf=None, agrupar=False):
    if not tabela_sql.startswith("basedosdados."):
        tabela_full = f"basedosdados.{tabela_sql}"
    else:
        tabela_full = tabela_sql
    
    # --- ESTRATÉGIA 1: AGREGAÇÃO (Visão Histórica) ---
    if agrupar and ("frota" in tabela_sql or "caged" in tabela_sql):
        # Aqui fazemos a mágica: o SQL soma tudo antes de enviar pra gente
        # Tentamos agrupar pelas colunas comuns de tempo e categoria
        query = f"""
        SELECT ano, mes, tipo_veiculo, SUM(quantidade) as quantidade 
        FROM `{tabela_full}`
        WHERE ano >= {ano_min}
        GROUP BY ano, mes, tipo_veiculo
        ORDER BY ano DESC, mes DESC
        """
        # Nota: Removemos id_municipio e sigla_uf para caber na memória
    
    # --- ESTRATÉGIA 2: DETALHADA (Visão Granular) ---
    else:
        query = f"SELECT * FROM `{tabela_full}` WHERE 1=1"
        if ano_min: query += f" AND ano >= {ano_min}"
        if uf: query += f" AND sigla_uf = '{uf}'"
        
        if "ano" in tabela_sql or "data" in tabela_sql: 
            try: query += " ORDER BY ano DESC"
            except: pass 
        
        query += " LIMIT 50000" 
    
    return bd.read_sql(query=query, billing_project_id=proj_id)

# --- ÁREA PRINCIPAL ---
st.title("📚 Catálogo Analítico de Dados Públicos")

if tabela_id:
    st.write(f"### Analisando: **{tabela_nome}**")
    
    if st.button("🚀 Carregar e Analisar Dados", type="primary"):
        with st.spinner("Consultando BigQuery..."):
            try:
                # Passamos o novo parâmetro 'agrupar_brasil'
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
            except Exception as e:
                st.error(f"Erro na consulta SQL: {e}")
                st.warning("Dica: O modo 'Agregado' funciona melhor em bases como Frota e CAGED. Em outras, tente desmarcar.")

    if 'df_analise' in st.session_state:
        df = st.session_state['df_analise']
        
        # --- NAVEGAÇÃO ---
        st.divider()
        opcoes_nav = ["📄 Dados Brutos"]
        if TEM_PYGWALKER: opcoes_nav.append("🎨 BI Self-Service")
        if TEM_SWEETVIZ: opcoes_nav.append("🍭 Relatório IA")
            
        escolha = st.radio("Escolha a Visualização:", opcoes_nav, horizontal=True)
        st.divider()
        
        # --- 1. DADOS ---
        if escolha == "📄 Dados Brutos":
            st.caption(f"Visualizando {len(df)} registros. (Modo Agregado: {agrupar_brasil})")
            st.dataframe(df, use_container_width=True)
            
        # --- 2. PYGWALKER ---
        elif escolha == "🎨 BI Self-Service":
            if len(df) == 0:
                st.warning("⚠️ Tabela vazia.")
            else:
                st.info("💡 Arraste 'data_referencia' para o Eixo X para ver a evolução temporal!")
                try:
                    df_safe = df.copy()
                    for col in df_safe.columns:
                        if df_safe[col].dtype == 'object':
                            df_safe[col] = df_safe[col].astype(str)
                    
                    pyg_html = pyg.walk(df_safe, return_html=True)
                    components.html(pyg_html, height=1000, scrolling=True)
                except Exception as e:
                    st.error(f"Erro no PyGWalker: {e}")

        # --- 3. SWEETVIZ ---
        elif escolha == "🍭 Relatório IA":
            st.markdown("### 🤖 Relatório de Inteligência Artificial")
            
            if st.button("📊 GERAR RELATÓRIO AGORA", type="primary"):
                with st.spinner("A IA está analisando..."):
                    try:
                        df_report = df.copy()
                        for col in df_report.columns:
                            if df_report[col].dtype == 'object':
                                df_report[col] = df_report[col].astype(str)
                        
                        analise = sv.analyze(df_report)
                        analise.show_html("relatorio_temp.html", open_browser=False, layout='vertical', scale=1.0)
                        
                        with open("relatorio_temp.html", 'r', encoding='utf-8') as f:
                            html_code = f.read()
                        
                        components.html(html_code, height=1100, scrolling=True)

                        st.download_button(
                            label="📥 Baixar Relatório Completo (.html)",
                            data=html_code,
                            file_name=f"Relatorio_{tabela_nome}.html",
                            mime="text/html"
                        )
                        
                    except Exception as e:
                        st.error(f"Erro técnico: {e}")

else:
    st.info("👈 Selecione uma base no menu lateral.")