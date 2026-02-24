# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 11:17:24 2026

@author: josej
"""
import os
from google.cloud import bigquery
import json

# --- AUTENTICAÇÃO ---
# Esta linha aponta para o seu "crachá" do Google Cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credenciais.json"

# Seu ID de projeto do Google Cloud
PROJECT_ID = "paineldadosabertos"

def sincronizar():
    print("🔄 Iniciando sincronização via Google Client Library...")
    
    # O cliente agora vai encontrar o arquivo JSON automaticamente
    client = bigquery.Client(project=PROJECT_ID)
    
    datasets_alvo = [
        'br_ibge_ipca', 
        'br_ibge_pib', 
        'br_me_caged', 
        'br_ms_sim', 
        'br_inep_censo_escolar',
        'br_ibge_populacao',
        'br_tse_eleicoes'
    ]
    
    novo_catalogo = {}
    
    try:
        for ds_id in datasets_alvo:
            print(f"📂 Acessando dataset: {ds_id}...")
            dataset_ref = bigquery.DatasetReference("basedosdados", ds_id)
            tabelas = client.list_tables(dataset_ref)
            
            prefixo = ds_id.split('_')[1].upper() if '_' in ds_id else "GERAL"
            mapa_temas = {
                "IBGE": "Economia e Sociedade (IBGE)",
                "ME": "Trabalho e Emprego",
                "MS": "Saúde Pública",
                "INEP": "Educação",
                "TSE": "Política e Eleições"
            }
            tema = mapa_temas.get(prefixo, f"Tema: {prefixo}")
            
            if tema not in novo_catalogo:
                novo_catalogo[tema] = {}
            if ds_id not in novo_catalogo[tema]:
                novo_catalogo[tema][ds_id] = {}
            
            for tabela in tabelas:
                tab_id = tabela.table_id
                if any(x in tab_id for x in ['dicionario', 'auxiliar', 'staging', 'schema']):
                    continue
                
                nome_amigavel = tab_id.replace("_", " ").title()
                novo_catalogo[tema][ds_id][nome_amigavel] = f"basedosdados.{ds_id}.{tab_id}"
        
        with open("catalogo_mvp.json", "w", encoding="utf-8") as f:
            json.dump(novo_catalogo, f, ensure_ascii=False, indent=4)
            
        print("\n✅ Sucesso! O arquivo catalogo_mvp.json foi criado com as tabelas reais.")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    sincronizar()