import pandas as pd
import os
import streamlit as st
from datetime import datetime

# NOMES DISTINTOS PARA NÃO MISTURAR
PATH_LOG = "nexus_performance.csv"    # O que aparece no Raio-X
PATH_ROTEIROS = "nexus_roteiros.csv"  # Onde a IA guarda os textos longos

def dashboard_performance_simples():
    # Removido o título daqui porque já está no seu app.py
    if not os.path.exists(PATH_LOG):
        st.info("Aguardando primeira mineração para gerar indicadores...")
        return

    try:
        # Lógica blindada contra "coisas nada a ver"
        df = pd.read_csv(PATH_LOG, on_bad_lines='skip', engine='python')
        
        if not df.empty:
            st.write(f"📊 **{len(df)}** registros encontrados no radar.")
            st.data_editor(
                df.tail(20),
                column_config={
                    "link_afiliado": st.column_config.LinkColumn("🛒 Link", display_text="Ver Loja")
                },
                use_container_width=True,
                hide_index=True
            )
    except Exception as e:
        st.error(f"Erro de integridade nos dados: {e}")
