import pandas as pd
import urllib.parse
from datetime import datetime
import streamlit as st
import random
import os
from groq import Groq

DATA_PATH = "dataset_nexus.csv"

# --- FUNÇÃO DE IA INTEGRADA ---
def gerar_ia_interna(prompt):
    try:
        client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role":"user","content": prompt}],
            temperature=0.7
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Erro na IA Interna: {e}"

def aplicar_seo_viral(produto, link_base, nicho):
    ganchos = ["O segredo de", "Pare tudo e veja este", "Minha melhor compra:", "Item indispensável:"]
    hashtags = ["#achadinhos", "#shopee", "#viral", "#utilidades", "#comprinhas"]
    # Horários estratégicos para as postagens
    horarios = [f"{h:02d}:{m:02d}" for h in range(8, 23) for m in [0, 15, 30, 45]]

    # --- IDENTIFICAÇÃO DE MERCADO ---
    if "shopee" in link_base.lower() or "shope.ee" in link_base.lower():
        mercado = "Shopee 🟠"
    elif "amazon" in link_base.lower():
        mercado = "Amazon 🔵"
    else:
        mercado = "Outro ⚪"

    try:
        aff_id = st.secrets.get("SHOPEE_ID", "18316451024") # Seu ID de Campanha
        
        if not os.path.exists(DATA_PATH):
            pd.DataFrame(columns=["data", "loja", "produto", "link_afiliado", "copy_funil", "roteiro", "horario_previsto", "status"]).to_csv(DATA_PATH, index=False)
        
        df = pd.read_csv(DATA_PATH)
        novas = []

        # Criar 10 roteiros virais
        prompt_roteiros = f"Aja como TikToker. Crie 10 roteiros curtos (3 cenas) para o produto {produto}. Sem negrito, separe por '###'."
        res_raw = gerar_ia_interna(prompt_roteiros)
        res_roteiros = res_raw.split("###")

        nome_limpo = produto.replace("*", "").replace("PRODUTO:", "").strip()
        
        # --- CORREÇÃO DE LINK: BUSCA REAL SHOPEE ---
        # Isso evita o erro "Loja falhou ao carregar"
        termo_busca = urllib.parse.quote(nome_limpo)
        link_real_shopee = f"https://shopee.com.br/search?keyword={termo_busca}"

        for i in range(10):
            # Link de busca otimizado com seu rastreio de afiliado
            link_track = f"{link_real_shopee}&utm_source=affiliate&utm_campaign={aff_id}&sub_id=V{i+1}"
            
            roteiro_final = res_roteiros[i].strip().replace("*", "") if i < len(res_roteiros) else "Cena 1: Gancho | Cena 2: Demonstração | Cena 3: CTA"

            novas.append({
                "data": datetime.now().strftime("%d/%m"),
                "loja": mercado,
                "produto": f"{nome_limpo} [V{i+1}]",
                "link_afiliado": link_track,
                "copy_funil": f"{random.choice(ganchos)} {nome_limpo}! ✨ {' '.join(random.sample(hashtags, 3))}",
                "roteiro": roteiro_final,
                "horario_previsto": horarios[i % len(horarios)],
                "status": "PRONTO"
            })
        
        pd.concat([df, pd.DataFrame(novas)], ignore_index=True).to_csv(DATA_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"Erro no Motor de Injeção: {e}")
        return False

def dashboard_performance_simples():
    st.header("📊 Raio-X de Performance")
    
    # --- ÁREA DE INJEÇÃO MANUAL (O ARSENAL DE RESERVA) ---
    with st.expander("➕ Injetar Link Manual (Link Direto)"):
        col1, col2 = st.columns(2)
        m_nome = col1.text_input("Nome do Produto Manual")
        m_link = col2.text_input("Link Direto da Shopee")
        if st.button("🚀 Injetar Manualmente"):
            if m_nome and m_link:
                if aplicar_seo_viral(m_nome, m_link, "Geral"):
                    st.success("✅ Produto injetado com sucesso!")
                    st.rerun()

    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        if "loja" not in df.columns: df["loja"] = "Shopee 🟠"

        # Métricas Rápidas
        c1, c2, c3 = st.columns(3)
        c1.metric("📦 Em Fila", len(df[df["status"]=="PRONTO"]))
        c2.metric("✅ Postados", len(df[df["status"]=="ENVIADO"]))
        c3.metric("🛒 Mercado Principal", "Shopee")

        st.subheader("📅 Cronograma de Postagens Diárias")
        
        # Monitor Editável
        colunas_monitor = ["data", "horario_previsto", "loja", "produto", "status", "link_afiliado"]
        
        st.data_editor(
            df[colunas_monitor].tail(40),
            column_config={
                "loja": st.column_config.TextColumn("Mercado", width="small"),
                "link_afiliado": st.column_config.LinkColumn("Link de Venda", display_text="Abrir 🛒"),
                "status": st.column_config.SelectboxColumn("Status", options=["PRONTO", "ENVIADO", "CANCELADO"])
            },
            disabled=["data", "loja"],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhum produto minerado ainda. Vá ao Scanner!")
