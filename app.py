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
st.set_page_config(layout="wide", page_title="Diagnóstico Final", page_icon="🧪")
st.title("🧪 Diagnóstico: Conexão Direta (Sem Arquivos)")

# --- PASSO 1: AUTENTICAÇÃO VIA MEMÓRIA ---
st.write("### 1. Tentando Autenticação Direta...")

try:
    # Verifica se os segredos existem
    if "gcp_service_account" not in st.secrets:
        st.error("❌ Erro Crítico: 'gcp_service_account' não encontrado nos Secrets!")
        st.stop() # Para tudo se não tiver senha

    # Cria as credenciais direto da memória (sem arquivo json)
    info_credenciais = dict(st.secrets["gcp_service_account"])
    credenciais = service_account.Credentials.from_service_account_info(info_credenciais)
    
    st.success(f"✅ Credenciais carregadas para o projeto: **{info_credenciais.get('project_id')}**")

except Exception as e:
    st.error(f"❌ Erro ao ler secrets: {e}")
    st.stop()

# --- PASSO 2: CONEXÃO COM BIGQUERY ---
st.write("### 2. Baixando Dados...")

if st.button("🚀 Testar Conexão Agora"):
    with st.spinner("Conectando ao Google..."):
        try:
            # Passa as credenciais EXPLICITAMENTE
            client = bigquery.Client(credentials=credenciais, project=credenciais.project_id)
            
            # Query ultra leve
            query = "SELECT * FROM `basedosdados.br_ibge_populacao.municipio` LIMIT 3"
            
            # ADICIONAMOS TIMEOUT: Se não responder em 15s, ele cancela
            job = client.query(query)
            result = job.result(timeout=15) # <--- O segredo anti-travamento
            df = result.to_dataframe()
            
            st.balloons()
            st.success("🎉 SUCESSO ABSOLUTO! O BigQuery respondeu!")
            st.dataframe(df)
            
        except Exception as e:
            st.error(f"❌ Falha: {e}")
            st.write("Se o erro mencionar 'db-dtypes', adicione ao requirements.txt!")