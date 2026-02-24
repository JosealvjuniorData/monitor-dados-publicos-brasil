import streamlit as st
import requests
import pandas as pd
import duckdb
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Self-Service BI Federal")
st.title("🛠️ Painel Self-Service de Dados Públicos")
st.markdown("Extração sob demanda + Motor SQL Dinâmico (DuckDB)")

# --- 1. EXTRAÇÃO DE DADOS ---
st.sidebar.header("1. Parâmetros de Extração")
api_key_input = st.sidebar.text_input("Chave da API (Portal da Transparência):", type="password")

# Seletores de data
d1 = st.sidebar.date_input("Data de Início:", value=datetime.today() - timedelta(days=30), format="DD/MM/YYYY")
d2 = st.sidebar.date_input("Data de Fim:", value=datetime.today(), format="DD/MM/YYYY")

# Trava de Segurança de BI (Evita o Erro 400 de Período Longo)
intervalo_dias = (d2 - d1).days
if intervalo_dias > 31:
    st.sidebar.error(f"⚠️ Atenção: O período selecionado tem {intervalo_dias} dias. A API do governo permite buscar no máximo 31 dias por vez.")

@st.cache_data(ttl=600)
def extrair_dados_governo(chave_api, data_inicio, data_fim):
    url = "https://api.portaldatransparencia.gov.br/api-de-dados/viagens"
    headers = {"chave-api-dados": chave_api}
    params = {
        "dataIdaDe": data_inicio, "dataIdaAte": data_fim,
        "dataRetornoDe": data_inicio, "dataRetornoAte": data_fim,
        "pagina": 1
    }
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=20)
        if resp.status_code == 200:
            dados = resp.json()
            if dados:
                df_bruto = pd.DataFrame(dados)
                
                for col in df_bruto.columns:
                    if not df_bruto.empty and isinstance(df_bruto[col].iloc[0], dict):
                        df_bruto[col] = df_bruto[col].apply(lambda x: x.get('nome') or str(x) if isinstance(x, dict) else x)
                
                if 'valorTotalViagem' in df_bruto.columns:
                    df_bruto['valorTotalViagem'] = pd.to_numeric(df_bruto['valorTotalViagem'].astype(str).str.replace(',', '.'), errors='coerce')
                    
                return df_bruto, None
            else:
                return pd.DataFrame(), "A API não possui registros processados para estas datas específicas."
        elif resp.status_code == 400:
            # Mostrando exatamente o que o governo está reclamando
            return pd.DataFrame(), f"Erro 400 (Requisição Inválida): A API recusou. Detalhes: {resp.text}"
        elif resp.status_code == 401:
            return pd.DataFrame(), "Sua Chave de API é inválida ou expirou."
        else:
            return pd.DataFrame(), f"Erro no portal (Status {resp.status_code}). Detalhes: {resp.text}"
    except Exception as e:
         return pd.DataFrame(), f"Erro de conexão: {e}"

if api_key_input:
    api_key = "".join(c for c in api_key_input if c.isalnum())
    
    # Só libera o botão de extrair se o intervalo for permitido
    if intervalo_dias <= 31:
        if st.sidebar.button("Extrair Lote de Dados", type="primary"):
            with st.spinner(f"Baixando dados do governo de {d1.strftime('%d/%m/%Y')} a {d2.strftime('%d/%m/%Y')}..."):
                df_dados, erro = extrair_dados_governo(api_key, d1.strftime("%d/%m/%Y"), d2.strftime("%d/%m/%Y"))
                st.session_state['df_base'] = df_dados
                st.session_state['erro_extracao'] = erro

# ... (O restante do código da seção 2 em diante permanece igualzinho) ...