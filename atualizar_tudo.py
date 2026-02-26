# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 00:50:02 2026

@author: josej
"""

import json
import os

ARQUIVO_CATALOGO = "catalogo_mvp.json"

print("🚀 Iniciando ATUALIZAÇÃO GERAL do Catálogo de Dados...")

# Dicionário DEFINITIVO com as melhores tabelas públicas do Brasil
# Estrutura: TEMA -> { Órgão: { Nome Amigável: ID_Tabela_BigQuery } }

catalogo_novo = {
    "1. Economia e Finanças": {
        "Índices de Inflação (IBGE/FGV)": {
            "IPCA - Nacional (Oficial)": "basedosdados.br_ibge_ipca.mes_brasil",
            "IPCA - Regional (Capitais)": "basedosdados.br_ibge_ipca.mes_rm",
            "IPCA-15 (Prévia Quinzenal)": "basedosdados.br_ibge_ipca15.mes_brasil",
            "INPC (Custo de Vida - Baixa Renda)": "basedosdados.br_ibge_inpc.mes_brasil",
            "IGP-M (Aluguéis - FGV)": "basedosdados.br_fgv_igp.igp_m_mes"
        },
        "Taxas e Moedas (BCB)": {
            "Taxa Selic (Meta e Real)": "basedosdados.br_bcb_taxa_selic.taxa_selic",
            "Dólar e Câmbio": "basedodados.br_bcb_taxa_cambio.taxa_cambio"
        },
        "PIB e Riqueza (IBGE)": {
            "PIB por Município (Série Completa)": "basedosdados.br_ibge_pib.municipio",
            "PIB por Estado (UF)": "basedosdados.br_ibge_pib.uf"
        }
    },
    "2. População e Sociedade": {
        "Censo e Estimativas (IBGE)": {
            "População por Município (Censo/Estimativa)": "basedosdados.br_ibge_populacao.municipio",
            "Perfil dos Domicílios (Censo 2010/2022)": "basedosdados.br_ibge_censo_demografico.setor_censitario_basico_2010"
        }
    },
    "3. Trabalho e Emprego": {
        "CAGED (Emprego Formal)": {
            "Novo Caged - Movimentações (Admissão/Demissão)": "basedosdados.br_me_caged.microdados_movimentacao",
            "Novo Caged - Saldo por Município": "basedosdados.br_me_caged.microdados_movimentacao_fora_prazo"
        },
        "RAIS (Vínculos Anuais)": {
            "Vínculos Empregatícios": "basedosdados.br_me_rais.microdados_vinculos"
        }
    },
    "4. Saúde Pública": {
        "Mortalidade e Nascimentos (DATASUS)": {
            "SIM - Mortalidade (Causas de Óbito)": "basedosdados.br_ms_sim.microdados",
            "SINASC - Nascimentos": "basedosdados.br_ms_sinasc.microdados"
        },
        "Epidemiologia": {
            "Casos de COVID-19 (Histórico)": "basedosdados.br_ms_vacinacao_covid19.microdados_vacinacao"
        }
    },
    "5. Segurança Pública": {
        "Dados Nacionais": {
            "Estatísticas de Segurança (Município)": "basedosdados.br_fbsp_seguranca.municipio"
        },
        "Dados Estaduais (Exemplos)": {
            "Crimes RJ (ISP)": "basedosdados.br_isp_estatisticas_seguranca.taxa_evolucao_mensal_uf",
            "Vítimas SP": "basedosdados.br_sp_ssp_seguranca.ocorrencias_mensais_municipio"
        }
    },
    "6. Meio Ambiente": {
        "Desmatamento e Clima": {
            "Desmatamento PRODES (Amazônia)": "basedosdados.br_inpe_prodes.desmatamento_municipio",
            "Focos de Calor (Queimadas - INPE)": "basedosdados.br_inpe_queimadas.microdados",
            "Emissões de Gases (SEEG)": "basedosdados.br_seeg_emissoes.municipio"
        }
    },
    "7. Transporte e Frota": {
        "DENATRAN": {
            "Frota de Veículos (Município)": "basedosdados.br_denatran_frota.municipio_tipo"
        }
    },
    "8. Eleições e Política": {
        "TSE": {
            "Bens dos Candidatos": "basedosdados.br_tse_eleicoes.bens_candidato",
            "Votação por Seção": "basedosdados.br_tse_eleicoes.resultados_partido_municipio"
        }
    }
}

print("💾 Substituindo arquivo antigo...")
with open(ARQUIVO_CATALOGO, "w", encoding="utf-8") as f:
    json.dump(catalogo_novo, f, ensure_ascii=False, indent=4)

print(f"✅ Sucesso! Catálogo atualizado com {sum(len(v) for v in catalogo_novo.values())} categorias principais.")
print("👉 Agora dê um 'Rerun' (tecla R) no seu Streamlit para ver os novos menus.")