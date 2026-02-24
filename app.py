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

st.set_page_config(layout="wide", page_title="Teste Geográfico", page_icon="🌎")
st.title("🌎 Diagnóstico: Localização e Permissão")

# --- 1. AUTENTICAÇÃO ---
st.write("### 1. Autenticação...")
try:
    if "gcp_service_account" not in st.secrets:
        st.error("Secrets não encontrados.")
        st.stop()

    info = dict(st.secrets["gcp_service_account"])
    credenciais = service_account.Credentials.from_service_account_info(info)
    st.success(f"✅ Conectado como: `{info.get('client_email')}` no projeto `{info.get('project_id')}`")

except Exception as e:
    st.error(f"Erro Auth: {e}")
    st.stop()

# --- 2. TESTE RÁPIDO (SELECT 1) ---
st.write("### 2. Teste de Vida (Sem Tabela)...")
if st.button("🚀 Testar SELECT 1"):
    with st.spinner("Verificando se sua conta pode rodar Jobs..."):
        try:
            # Forçamos a localização US (onde o basedosdados vive)
            client = bigquery.Client(credentials=credenciais, project=credenciais.project_id, location="US")
            
            # Query que não custa nada e não acessa disco
            query = "SELECT 'Estou vivo!' as status"
            
            # Timeout agressivo de 5 segundos. Se não for rápido, tem erro de conta.
            job = client.query(query)
            result = job.result(timeout=5) 
            
            st.success(f"🎉 SUCESSO! O BigQuery respondeu: {result.to_dataframe().iloc[0,0]}")
            st.info("Isso prova que sua Service Account TEM permissão de rodar Jobs!")

        except Exception as e:
            st.error(f"❌ Falha no SELECT 1: {e}")
            st.warning("⚠️ Se falhou aqui, sua Service Account no Google Cloud não tem a permissão 'BigQuery Job User' ou a API não está habilitada.")

# --- 3. TESTE DA TABELA REAL ---
st.write("### 3. Teste da Tabela Real...")
if st.button("🚀 Baixar Base dos Dados"):
    with st.spinner("Baixando dados reais nos EUA..."):
        try:
            client = bigquery.Client(credentials=credenciais, project=credenciais.project_id, location="US")
            
            # Usando REST API para evitar bloqueio de firewall
            query = "SELECT * FROM `basedosdados.br_ibge_populacao.municipio` LIMIT 5"
            
            job = client.query(query)
            # create_bqstorage_client=False é CRUCIAL para evitar travamento em nuvem grátis
            df = job.to_dataframe(create_bqstorage_client=False)
            
            st.balloons()
            st.dataframe(df)
            
        except Exception as e:
            st.error(f"❌ Falha na Tabela: {e}")