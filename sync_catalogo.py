# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 11:17:24 2026

@author: josej
"""
# -*- coding: utf-8 -*-
import os
import json
from google.cloud import bigquery
import sys

# --- CONFIGURAÇÃO PARA O GITHUB ACTIONS ---
# O GitHub Actions vai gerar o 'credenciais.json' temporariamente. 
# Essa linha garante que o BigQuery saiba onde procurar.
if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credenciais.json"

PROJECT_ID = "paineldadosabertos" # Mantivemos o seu Project ID original

def validar_catalogo():
    print("🤖 Iniciando Robô de Validação do Catálogo...")
    
    # 1. Tenta conectar no BigQuery
    try:
        client = bigquery.Client(project=PROJECT_ID)
        print("✅ Conexão com BigQuery estabelecida.")
    except Exception as e:
        print(f"❌ Erro Crítico de Autenticação: {e}")
        sys.exit(1) # Para o robô

    # 2. Abre o catálogo atual
    try:
        with open("catalogo_mvp.json", "r", encoding="utf-8") as f:
            catalogo = json.load(f)
    except FileNotFoundError:
        print("❌ Erro: Arquivo 'catalogo_mvp.json' não encontrado na pasta.")
        sys.exit(1)

    print("\n🔍 Escaneando links das tabelas...")
    erros = 0
    tabelas_quebradas = []

    # 3. Testa link por link
    for tema, categorias in catalogo.items():
        for categoria, tabelas in categorias.items():
            for nome_tabela, id_tabela in tabelas.items():
                
                # Garante que o ID tem o prefixo correto
                full_id = id_tabela if id_tabela.startswith("basedosdados.") else f"basedosdados.{id_tabela}"
                
                try:
                    # Tenta acessar os metadados da tabela na nuvem
                    client.get_table(full_id)
                    print(f"  [OK] {nome_tabela}")
                except Exception:
                    print(f"  [🚨 ERRO] {nome_tabela} -> ID não encontrado: {full_id}")
                    tabelas_quebradas.append(f"{nome_tabela} ({full_id})")
                    erros += 1

    # 4. Relatório Final
    print(f"\n🏁 Fim da varredura. Total de links testados e quebrados: {erros}")
    
    # Se houver erros, forçamos o script a "falhar" (Exit 1). 
    # Isso faz o GitHub Actions enviar um e-mail de alerta para você!
    if erros > 0:
        print("\n⚠️ ALERTA: As seguintes tabelas precisam ter seus IDs atualizados no JSON:")
        for t in tabelas_quebradas:
            print(f" - {t}")
        sys.exit(1) 
    else:
        print("✨ Tudo perfeito! Seu catálogo está 100% saudável.")

if __name__ == "__main__":
    validar_catalogo()