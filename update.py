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
            messages=[{"role":"user","content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

def aplicar_seo_viral(produto, link_base, nicho):
    ganchos = ["O segredo de", "Pare tudo e veja este", "Minha melhor compra:", "Item indispensável:"]
    hashtags = ["#achadinhos", "#shopee", "#viral", "#utilidades", "#comprinhas"]
    # 30 horários para suportar a mineração em massa
    horarios = [f"{h:02d}:{m:02d}" for h in range(8, 23) for m in [0, 30]] 

    # --- IDENTIFICAÇÃO DE MERCADO ---
    if "shopee.com.br" in link_base or "shope.ee" in link_base:
        mercado = "Shopee 🟠"
    elif "amazon.com" in link_base:
        mercado = "Amazon 🔵"
    elif "mercadolivre.com" in link_base:
        mercado = "M. Livre 🟡"
    else:
        mercado = "Outro ⚪"

    # Trava de Segurança
    if mercado != "Shopee 🟠":
        st.error(f"❌ O Nexus está em modo Shopee. Link de {mercado} bloqueado.")
        return False

    try:
        aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
        if not os.path.exists(DATA_PATH):
            pd.DataFrame(columns=["data", "loja", "produto", "link_afiliado", "copy_funil", "roteiro", "horario_previsto", "status"]).to_csv(DATA_PATH, index=False)
        
        df = pd.read_csv(DATA_PATH)
        novas = []

        prompt_roteiros = f"Aja como TikToker. Crie 10 roteiros curtos (3 cenas) para {produto}. Sem negrito, separe por '###'."
        res_raw = gerar_ia_interna(prompt_roteiros)
        res_roteiros = res_raw.split("###")

        nome_limpo = produto.replace("*", "").replace("PRODUTO:", "").strip()

        for i in range(10):
            link_track = f"{link_base}?sp_atk=nexus&utm_source=affiliate&utm_campaign={aff_id}&sub_id=V{i+1}"
            
            novas.append({
                "data": datetime.now().strftime("%d/%m"),
                "loja": mercado,
                "produto": f"{nome_limpo} [V{i+1}]",
                "link_afiliado": link_track,
                "copy_funil": f"{random.choice(ganchos)} {nome_limpo}! ✨ {' '.join(random.sample(hashtags, 3))}",
                "roteiro": res_roteiros[i].strip().replace("*", "") if i < len(res_roteiros) else "Cena 1: Gancho | Cena 2: Uso",
                "horario_previsto": horarios[i % len(horarios)],
                "status": "PRONTO"
            })
        
        pd.concat([df, pd.DataFrame(novas)], ignore_index=True).to_csv(DATA_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"Erro no Motor: {e}")
        return False

def dashboard_performance_simples():
    st.header("📊 Raio-X de Performance")
    
    # ENTRADA MANUAL (O que você pediu para o Arsenal)
    with st.expander("➕ Injetar Link Manualmente"):
        col1, col2 = st.columns(2)
        m_nome = col1.text_input("Nome do Produto")
        m_link = col2.text_input("Cole o Link da Shopee")
        if st.button("🚀 Injetar Manual"):
            if m_nome and m_link:
                if aplicar_seo_viral(m_nome, m_link, "Geral"):
                    st.success("Injetado com sucesso!")
                    st.rerun()

    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        if "loja" not in df.columns: df["loja"] = "Shopee 🟠"

        # Tabela com Link Clicável e Coluna de Mercado
        st.data_editor(
            df[["data", "horario_previsto", "loja", "produto", "status", "link_afiliado"]].tail(30),
            column_config={
                "loja": st.column_config.TextColumn("Mercado", width="small"),
                "link_afiliado": st.column_config.LinkColumn("Link", display_text="Abrir 🛒")
            },
            disabled=True,
            use_container_width=True,
            hide_index=True
        )
