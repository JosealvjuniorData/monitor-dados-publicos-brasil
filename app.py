# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 11:17:24 2026

@author: josej
"""
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(layout="wide", page_title="Diagnóstico Final", page_icon="🔧")
st.title("🔧 Diagnóstico: Modo de Compatibilidade (REST API)")

st.write("### 1. Autenticação...")

# --- AUTENTICAÇÃO ---
try:
    if "gcp_service_account" not in st.secrets:
        st.error("❌ Secrets não encontrados.")
        st.stop()

    info_credenciais = dict(st.secrets["gcp_service_account"])
    credenciais = service_account.Credentials.from_service_account_info(info_credenciais)
    st.success(f"✅ Credenciais OK! Projeto: **{info_credenciais.get('project_id')}**")

except Exception as e:
    st.error(f"❌ Erro de Auth: {e}")
    st.stop()

# --- CONEXÃO ---
st.write("### 2. Baixando Dados (Modo Seguro)...")

if st.button("🚀 Testar Conexão Agora"):
    with st.spinner("Conectando via REST API (sem gRPC)..."):
        try:
            # Cliente Padrão
            client = bigquery.Client(credentials=credenciais, project=credenciais.project_id)
            
            # Query simples
            query = "SELECT * FROM `basedosdados.br_ibge_populacao.municipio` LIMIT 5"
            st.info(f"Enviando pedido: `{query}`")
            
            job = client.query(query)
            
            # --- O PULO DO GATO ---
            # create_bqstorage_client=False -> Força usar HTTPS normal em vez de gRPC
            # Isso evita o travamento em firewalls de nuvem
            df = job.to_dataframe(create_bqstorage_client=False)
            
            st.balloons()
            st.success("🎉 SUCESSO! Dados baixados via REST API!")
            st.dataframe(df)
            
        except Exception as e:
            st.error(f"❌ Falha: {e}")
            st.markdown("---")
            st.warning("Se funcionou agora, o problema era o bloqueio de gRPC na nuvem.")