# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 10:17:24 2026

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

# --- IMPORTAÇÃO BLINDADA ---
try:
    import pygwalker as pyg
    from pygwalker.api.streamlit import StreamlitRenderer
    TEM_PYGWALKER = True
except ImportError:
    TEM_PYGWALKER = False

try:
    import pkg_resources 
    import sweetviz as sv
    TEM_SWEETVIZ = True
    ERRO_SWEETVIZ = None
except ImportError:
    try:
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

# --- FUNÇÃO DE LIMPEZA 'BLINDADA' ---
def sanitizar_df(df_original):
    """
    Remove tipos complexos do BigQuery.
    Estratégia: Converte tipos desconhecidos para STRING ou FLOAT.
    """
    df = df_original.copy()
    
    for col in df.columns:
        # Verifica o tipo da coluna
        dtype_str = str(df[col].dtype)
        
        # 1. Numéricos viram Float (seguro)
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].astype(float)
            
        # 2. Se for datetime OFICIAL do Pandas, apenas tira o fuso
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
             df[col] = df[col].dt.tz_localize(None)
             
        # 3. Se for 'dbdate', 'object' ou qualquer coisa estranha
        else:
            # Tenta converter para datetime primeiro
            try:
                col_converted = pd.to_datetime(df[col], errors='coerce')
                # Se a conversão funcionou e não gerou tudo NaT
                if not col_converted.isna().all():
                     df[col] = col_converted
                     df[col] = df[col].dt.tz_localize(None)
                else:
                     # Se falhar, VIRA TEXTO (String)
                     # PyGWalker aceita datas como texto ('2023-01-01') sem travar
                     df[col] = df[col].astype(str)
                     df[col] = df[col].replace({'nan': None, 'NaT': None, '<NA>': None, 'None': None})
            except:
                # Fallback final: Texto puro
                df[col] = df[col].astype(str)
                df[col] = df[col].replace({'nan': None, 'NaT': None, '<NA>': None, 'None': None})

    return df

# --- FUNÇÃO MÁGICA: LINK PARA NOVA ABA ---
def criar_link_nova_aba(html_content, titulo_botao, nome_arquivo):
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
# --- NOVOS AVISOS DA BARRA LATERAL ---
st.sidebar.divider()
st.sidebar.markdown("### ℹ️ Sobre")
st.sidebar.info(
    "**Fonte de Dados:** Este painel utiliza a camada gratuita da 'Base dos Dados'. "
    "Alguns indicadores podem apresentar atraso de 3 a 12 meses em relação à data atual "
    "devido às políticas de acesso da API."
)
st.sidebar.markdown(
    """
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; border: 1px solid #d6d6d6;">
        📧 <strong>Tem sugestão de nova base?</strong><br>
        Entre em contato:<br>
        <a href="mailto:josealvjunior@gmail.com" style="text-decoration: none; color: #0068c9; font-weight: bold;">
            josealvjunior@gmail.com
        </a>
    </div>
    <br>
    """, 
    unsafe_allow_html=True
)
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

# --- EXTRAÇÃO INTELIGENTE ---
@st.cache_data(ttl=3600)
def extrair_dados(tabela_sql, proj_id, ano_min=None, uf=None, agrupar=False):
    tabela_full = f"basedosdados.{tabela_sql}" if not tabela_sql.startswith("basedosdados.") else tabela_sql
    client = bigquery.Client(credentials=credenciais, project=proj_id, location="US")
    
    # 1. Espião de colunas
    try:
        table_ref = client.get_table(tabela_full)
        colunas_existentes = [c.name for c in table_ref.schema]
    except:
        colunas_existentes = []

    # 2. Lógica Específica
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
        # 3. Lógica Genérica
        query = f"SELECT * FROM `{tabela_full}` WHERE 1=1"
        if ano_min and 'ano' in colunas_existentes: query += f" AND ano >= {ano_min}"
        if uf and 'sigla_uf' in colunas_existentes: query += f" AND sigla_uf = '{uf}'"
        
        if 'ano' in colunas_existentes and 'mes' in colunas_existentes:
            query += " ORDER BY ano DESC, mes DESC"
        elif 'ano' in colunas_existentes:
            query += " ORDER BY ano DESC"

        query += " LIMIT 5000" 
    
    try:
        job = client.query(query)
        df = job.to_dataframe(create_bqstorage_client=False)
        return df
    except Exception as e:
        raise Exception(f"Erro SQL: {e}")

# --- ÁREA PRINCIPAL ---
st.title("📚 Monitor de Dados Públicos")

if tabela_id:
    st.write(f"### 📂 Base: **{tabela_nome}**")
    
    if st.button("🚀 Carregar Dados", type="primary"):
        with st.spinner("Baixando dados da nuvem (isso pode levar alguns segundos)..."):
            try:
                # Aqui o sistema TENTA extrair os dados normalmente
                df = extrair_dados(tabela_id, project_id, ano_minimo, sigla_uf, agrupar_brasil)
                
                # Se der certo, ele segue o fluxo normal (mantenha o código que você já tem aqui)
                st.success(f"✅ Dados carregados com sucesso! ({len(df)} linhas)")
                # Tenta criar data de referência
                if 'ano' in df.columns and 'mes' in df.columns:
                    try:
                        df['data_referencia'] = pd.to_datetime(df['ano'].astype(str) + '-' + df['mes'].astype(str) + '-01', errors='coerce')
                        df = df.sort_values('data_referencia')
                    except: pass
                
                st.session_state['df_analise'] = df
                st.success(f"Sucesso! {len(df)} linhas carregadas.")
            except Exception as e:
                # Se o código "quebrar", ele cai aqui no EXCEPT
                erro_str = str(e)
                
                # Verifica se o erro foi o famoso "404 Not Found" da Base dos Dados
                if "Not found" in erro_str or "404" in erro_str:
                    st.warning(f"⚠️ **Atenção:** A tabela `{tabela_id}` não está mais disponível neste endereço.")
                    st.info("💡 **O que aconteceu?** A Base dos Dados pode ter atualizado ou renomeado esta tabela. "
                            "Nossa equipe técnica (seu robô no GitHub 🤖) já foi notificada para corrigir este link "
                            "na próxima atualização. Por favor, tente outra base do catálogo!")
                else:
                    # Se for qualquer outro erro (ex: internet caiu, limite de cota), mostra o erro real
                    st.error(f"❌ Ocorreu um erro inesperado ao conectar com a Base dos Dados: {erro_str}")
                
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
                    st.info("💡 Clique no botão verde para abrir em tela cheia.")
                    
                    # --- APLICA A LIMPEZA ANTES DE TUDO ---
                    df_limpo = sanitizar_df(df)
                    
                    html_pyg = pyg.to_html(df_limpo)
                    st.markdown(criar_link_nova_aba(html_pyg, "Abrir BI em Tela Cheia", "bi_analise.html"), unsafe_allow_html=True)
                    
                    st.write("---")
                    st.write("**Versão Embarcada:**")

                    renderer = StreamlitRenderer(df_limpo, spec="./gw_config.json", spec_io_mode="RW")
                    renderer.explorer()
                    
                except Exception as e:
                    st.error(f"Erro PyGWalker: {e}")

        elif escolha == "🍭 Relatório Automático":
             if TEM_SWEETVIZ:
                if st.button("Gerar Relatório (IA)"):
                    with st.spinner("Analisando dados..."):
                        # --- APLICA A LIMPEZA ANTES DE TUDO ---
                        df_limpo = sanitizar_df(df)
                        
                        analise = sv.analyze(df_limpo)
                        analise.show_html("relatorio.html", open_browser=False)
                        
                        with open("relatorio.html", 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        st.success("Relatório pronto!")
                        st.markdown(criar_link_nova_aba(html_content, "Abrir Relatório Completo", "relatorio_ia.html"), unsafe_allow_html=True)
                        st.write("---")
                        components.html(html_content, height=800, scrolling=True)

else:
    st.info("👈 Selecione uma base no menu lateral.")