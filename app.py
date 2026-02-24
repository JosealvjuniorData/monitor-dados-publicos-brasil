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
from google.cloud import bigquery
from google.oauth2 import service_account

# --- CONFIGURAÇÃO DA PÁGINA (Primeira coisa a rodar) ---
st.set_page_config(layout="wide", page_title="Monitor MVP", page_icon="🚀")

st.title("🚀 Monitor de Dados - Modo de Diagnóstico")

# --- PASSO 1: DIAGNÓSTICO DE CREDENCIAIS ---
st.write("### 1. Verificando Credenciais...")

if os.path.exists("credenciais.json"):
    st.success("✅ Arquivo 'credenciais.json' encontrado na raiz!")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credenciais.json"
else:
    st.warning("⚠️ Arquivo não encontrado. Tentando criar via Secrets...")
    if "gcp_service_account" in st.secrets:
        try:
            with open("credenciais.json", "w") as f:
                json.dump(dict(st.secrets["gcp_service_account"]), f)
            st.success("✅ Arquivo 'credenciais.json' criado com sucesso via Secrets!")
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credenciais.json"
        except Exception as e:
            st.error(f"❌ Erro ao criar credenciais: {e}")
    else:
        st.error("❌ Segredo 'gcp_service_account' não encontrado no Streamlit Cloud.")

# --- PASSO 2: TESTE DE CONEXÃO ---
st.write("### 2. Teste de Conexão com BigQuery...")

if st.button("Testar Conexão Agora"):
    try:
        # Tenta conectar e baixar APENAS 5 linhas de uma tabela pública leve
        client = bigquery.Client()
        query = "SELECT * FROM `basedosdados.br_ibge_populacao.municipio` LIMIT 5"
        
        st.info(f"Executando query: `{query}`")
        
        job = client.query(query)
        df = job.to_dataframe()
        
        st.success("🎉 SUCESSO! Conexão estabelecida.")
        st.dataframe(df)
        
    except Exception as e:
        st.error(f"❌ Falha na conexão: {e}")
        st.write("Dica: Verifique se a Service Account tem permissão 'BigQuery Job User'.")

st.write("---")
st.write("Se você vê esta tela, o Streamlit NÃO está travado. O problema estava no código anterior.")