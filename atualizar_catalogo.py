# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 23:29:19 2026

@author: josej
"""

import json
import basedosdados as bd
import os

# Configuração para não pedir projeto toda hora (opcional se já tiver env)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credenciais.json"

print("⏳ Iniciando atualização do catálogo com bases Premium...")

# Dicionário CURADO com as melhores bases do Brasil (IDs reais do BigQuery)
# Estrutura: TEMA -> { Órgão: { Nome Amigável: ID_da_Tabela } }
novos_dados = {
    "Economia e Sociedade (IBGE)": {
        "IBGE - Censo Demográfico": {
            "População por Município (Série Histórica)": "br_ibge_populacao.municipio",
            "PIB por Município": "br_ibge_pib.municipio"
        },
        "IBGE - Índices de Preços": {
            "IPCA (Inflação) - Mesal": "br_ibge_ipca.mes_brasil"
        }
    },
    "Trabalho e Emprego": {
        "Ministério da Economia (CAGED)": {
            "Novo Caged - Movimentações (Microdados)": "br_me_caged.microdados_movimentacao",
            "Novo Caged - Saldos por Município": "br_me_caged.microdados_movimentacao_fora_prazo" 
        },
        "RAIS - Vínculos": {
            "Vínculos Empregatícios (Amostra 1%)": "br_me_rais.microdados_vinculos"
        }
    },
    "Saúde Pública": {
        "Ministério da Saúde (DATASUS)": {
            "Mortalidade (SIM) - Causas de Óbito": "br_ms_sim.microdados",
            "Nascimentos (SINASC)": "br_ms_sinasc.microdados",
            "Vacinação COVID-19 (Microdados)": "br_ms_vacinacao_covid19.microdados_vacinacao"
        }
    },
    "Segurança Pública": {
        "Fórum Brasileiro de Segurança": {
            "Estatísticas de Segurança (Município)": "br_fbsp_seguranca.municipio"
        },
        "ISP (Rio de Janeiro)": {
            "Crimes por Delegacia (RJ)": "br_isp_estatisticas_seguranca.taxa_evolucao_mensal_uf"
        }
    },
    "Meio Ambiente e Clima": {
        "INPE (Desmatamento)": {
            "Desmatamento Prodes (Amazônia)": "br_inpe_prodes.desmatamento_municipio",
            "Focos de Queimadas": "br_inpe_queimadas.microdados"
        },
        "SEEG (Emissões)": {
            "Emissões de Gases (Município)": "br_seeg_emissoes.municipio"
        }
    },
    "Transporte e Veículos": {
        "DENATRAN": {
            "Frota de Veículos por Município": "br_denatran_frota.municipio_tipo"
        }
    },
    "Política e Eleições": {
        "TSE (Eleições)": {
            "Bens dos Candidatos": "br_tse_eleicoes.bens_candidato",
            "Resultados por Seção Eleitoral": "br_tse_eleicoes.resultados_partido_municipio"
        },
        "Câmara dos Deputados": {
            "Gastos da Cota Parlamentar": "br_camara_dados_abertos.cota_parlamentar"
        }
    },
    "Energia e Infraestrutura": {
        "ANEEL": {
            "Tarifas de Energia (Residencial)": "br_aneel_tarifas.distribuidoras_residenciais"
        }
    }
}

arquivo_saida = "catalogo_mvp.json"

print("💾 Salvando novo catálogo turbinado...")
with open(arquivo_saida, "w", encoding="utf-8") as f:
    json.dump(novos_dados, f, ensure_ascii=False, indent=4)

print(f"✅ Sucesso! O arquivo '{arquivo_saida}' foi atualizado com {len(novos_dados)} temas.")
print("👉 Agora dê um 'Rerun' no seu site Streamlit.")