import pandas as pd
import urllib.parse
from datetime import datetime
import streamlit as st
import random
import os
from groq import Groq

DATA_PATH = "dataset_nexus.csv"

# --- ADAPTADO PARA EVITAR ERRO DE TOKENIZACAO ---
def aplicar_seo_viral(produto, link_base, nicho):
    try:
        aff_id = "18316451024" 
        nome_limpo = produto.split('|')[0].replace("PRODUTO:", "").replace("NOME:", "").strip()
        
        # 1. Leitura Robusta: ignora linhas sujas se existirem
        if os.path.exists(DATA_PATH):
            try:
                df = pd.read_csv(DATA_PATH, on_bad_lines='skip', engine='python')
            except:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()

        novas = []
        res_raw = gerar_ia_interna(f"Crie 10 roteiros curtos para {nome_limpo}. Separe por '###'.")
        res_roteiros = res_raw.split("###")

        for i in range(10):
            link_track = f"https://shopee.com.br/search?keyword={urllib.parse.quote(nome_limpo)}&utm_source=affiliate&utm_campaign={aff_id}&sub_id=V{i+1}"
            
            # Limpeza rápida do roteiro para evitar quebras de CSV
            roteiro_limpo = res_roteiros[i].strip().replace('"', "'") if i < len(res_roteiros) else "Cena 1: Gancho"

            novas.append({
                "data": datetime.now().strftime("%d/%m"),
                "loja": "Shopee 🟠",
                "produto": f"{nome_limpo} [V{i+1}]",
                "link_afiliado": link_track,
                "copy_funil": f"Olha esse achadinho: {nome_limpo}! ✨",
                "roteiro": roteiro_limpo, # Texto protegido
                "horario_previsto": f"{random.randint(8,22)}:{random.choice(['00','30'])}",
                "status": "PRONTO"
            })
        
        # 2. Salvamento Seguro: usa quoting para proteger as vírgulas dentro do texto
        new_df = pd.DataFrame(novas)
        df_final = pd.concat([df, new_df], ignore_index=True)
        df_final.to_csv(DATA_PATH, index=False, quoting=1) # 1 = csv.QUOTE_ALL
        
        return True
    except Exception as e:
        st.error(f"Erro no SEO: {e}")
        return False

def dashboard_performance_simples():
    st.header("📊 Raio-X de Performance")
    if os.path.exists(DATA_PATH):
        try:
            # 3. Leitura com proteção para o dashboard
            df = pd.read_csv(DATA_PATH, on_bad_lines='skip', engine='python')
            st.data_editor(
                df.tail(40),
                column_config={"link_afiliado": st.column_config.LinkColumn("Link", display_text="Abrir 🛒")},
                use_container_width=True, hide_index=True
            )
        except Exception as e:
            st.error(f"Erro crítico no CSV: {e}. Sugestão: Delete o arquivo {DATA_PATH} para resetar.")
