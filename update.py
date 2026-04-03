import pandas as pd
import urllib.parse
from datetime import datetime
import streamlit as st
import random
import os
from groq import Groq

DATA_PATH = "dataset_nexus.csv"

def gerar_ia_interna(prompt):
    try:
        client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"user","content": prompt}],
            temperature=0.7
        )
        return res.choices[0].message.content
    except: return "Cena 1: Gancho | Cena 2: Uso | Cena 3: CTA"

def aplicar_seo_viral(produto, link_base, nicho):
    try:
        # SEU ID DE AFILIADO
        aff_id = "18316451024" 
        
        # Limpeza do nome para a busca não falhar
        nome_limpo = produto.split('|')[0].replace("PRODUTO:", "").replace("NOME:", "").strip()
        if nome_limpo[0].isdigit() and "." in nome_limpo[:3]:
            nome_limpo = nome_limpo.split(' ', 1)[-1]

        # Geração da URL de Busca Real (Evita erro de loja)
        termo_busca = urllib.parse.quote(nome_limpo)
        link_final_base = f"https://shopee.com.br/search?keyword={termo_busca}"

        df = pd.read_csv(DATA_PATH) if os.path.exists(DATA_PATH) else pd.DataFrame()
        novas = []

        res_raw = gerar_ia_interna(f"Crie 10 roteiros curtos para {nome_limpo}. Separe por '###'.")
        res_roteiros = res_raw.split("###")

        for i in range(10):
            # Injeção do rastro de comissão via UTM
            link_track = f"{link_final_base}&utm_source=affiliate&utm_campaign={aff_id}&sub_id=V{i+1}"
            
            novas.append({
                "data": datetime.now().strftime("%d/%m"),
                "loja": "Shopee 🟠",
                "produto": f"{nome_limpo} [V{i+1}]",
                "link_afiliado": link_track,
                "copy_funil": f"Olha esse achadinho: {nome_limpo}! ✨ #shopee #viral",
                "roteiro": res_roteiros[i].strip() if i < len(res_roteiros) else "Cena 1: Gancho",
                "horario_previsto": f"{random.randint(8,22)}:{random.choice(['00','30'])}",
                "status": "PRONTO"
            })
        
        pd.concat([df, pd.DataFrame(novas)], ignore_index=True).to_csv(DATA_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"Erro: {e}")
        return False

def dashboard_performance_simples():
    st.header("📊 Raio-X de Performance")
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        st.data_editor(
            df.tail(40),
            column_config={"link_afiliado": st.column_config.LinkColumn("Link", display_text="Abrir 🛒")},
            use_container_width=True, hide_index=True
        )
