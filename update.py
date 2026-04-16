import pandas as pd
import os
import streamlit as st
from datetime import datetime

# NOMES DISTINTOS PARA NÃO MISTURAR
PATH_LOG = "nexus_performance.csv"    # O que aparece no Raio-X
PATH_ROTEIROS = "nexus_roteiros.csv"  # Onde a IA guarda os textos longos

def dashboard_performance_simples():
    # Verifica se o arquivo existe e tem dados
    if not os.path.exists(PATH_LOG):
        st.info("📊 Aguardando primeira mineração para gerar indicadores...")
        return

    try:
        df = pd.read_csv(PATH_LOG, on_bad_lines='skip', engine='python')
        
        if not df.empty:
            st.write(f"✅ **{len(df)}** produtos minerados e prontos para o Estúdio.")
            
            # Gráfico Rápido de Calor (Temperatura de Venda)
            if 'calor' in df.columns:
                st.line_chart(df['calor'], height=150)

            st.data_editor(
                df.tail(20),
                column_config={
                    "link": st.column_config.LinkColumn("🛒 Link Blindado", display_text="Afiliado 18316451024")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Base de dados vazia. Inicie o Scanner!")
    except Exception as e:
        st.error(f"Erro de integridade nos dados: {e}")

# --- FUNÇÃO QUE ALIMENTA O DASHBOARD ---
def registrar_mineracao(nome, link, calor):
    """Salva os dados minerados no CSV para o Dashboard ler"""
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    novo_dado = pd.DataFrame([[data_hoje, nome, link, calor]], 
                            columns=['data', 'produto', 'link', 'calor'])
    
    if not os.path.exists(PATH_LOG):
        novo_dado.to_csv(PATH_LOG, index=False)
    else:
        novo_dado.to_csv(PATH_LOG, mode='a', header=False, index=False)

# --- FUNÇÃO QUE EVITA O ERRO NO ESTÚDIO ---
def aplicar_seo_viral(nome, link, tags):
    """Registra o rastro de SEO do produto"""
    registrar_mineracao(nome, link, 99) # Registra como calor máximo
    return True
