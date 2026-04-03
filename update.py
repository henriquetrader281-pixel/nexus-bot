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
            messages=[{"role":"user","content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

def aplicar_seo_viral(produto, link_base, nicho):
    ganchos = ["O segredo de", "Pare tudo e veja este", "Minha melhor compra:", "Item indispensável:"]
    hashtags = ["#achadinhos", "#shopee", "#viral", "#utilidades", "#comprinhas"]
    horarios = ["08:30", "11:15", "12:45", "15:00", "17:30", "18:50", "20:10", "21:30", "22:45", "23:15"]

    # --- IDENTIFICAÇÃO DE MERCADO (Pronto para Expansão) ---
    if "shopee.com.br" in link_base or "shope.ee" in link_base:
        mercado = "Shopee 🟠"
    elif "amazon.com" in link_base:
        mercado = "Amazon 🔵"
    elif "mercadolivre.com" in link_base:
        mercado = "M. Livre 🟡"
    else:
        mercado = "Outro ⚪"

    # Trava temporária: enquanto você foca só em Shopee
    if mercado != "Shopee 🟠":
        st.warning(f"⚠️ Atenção: O Nexus está em modo 'Shopee Only'. Link de {mercado} detectado.")
        # Se quiser bloquear de vez, descomente a linha abaixo:
        # return False

    try:
        aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
        
        if not os.path.exists(DATA_PATH):
            pd.DataFrame(columns=["data", "loja", "produto", "link_afiliado", "copy_funil", "roteiro", "horario_previsto", "status"]).to_csv(DATA_PATH, index=False)
        
        df = pd.read_csv(DATA_PATH)
        novas = []

        # Prompt focado em 10 variações (mais rápido e assertivo)
        prompt_roteiros = f"Aja como TikToker. Crie 10 roteiros curtos para {produto} no nicho {nicho}. Sem negrito, separe por '###'."
        res_raw = gerar_ia_interna(prompt_roteiros)
        res_roteiros = res_raw.split("###")

        nome_limpo = produto.replace("*", "").replace("PRODUTO:", "").strip()

        for i in range(10):
            # Gera link de rastreio apenas se for Shopee, senão mantém o original
            if "Shopee" in mercado:
                link_final = f"{link_base}?sp_atk=nexus&utm_source=affiliate&utm_campaign={aff_id}&sub_id=V{i+1}"
            else:
                link_final = link_base

            novas.append({
                "data": datetime.now().strftime("%d/%m"),
                "loja": mercado,
                "produto": f"{nome_limpo} [V{i+1}]",
                "link_afiliado": link_final,
                "copy_funil": f"{random.choice(ganchos)} {nome_limpo}! ✨ {' '.join(random.sample(hashtags, 3))}",
                "roteiro": res_roteiros[i].strip().replace("*", "") if i < len(res_roteiros) else "Cena 1: Gancho | Cena 2: Uso",
                "horario_previsto": horarios[i],
                "status": "PRONTO"
            })
        
        pd.concat([df, pd.DataFrame(novas)], ignore_index=True).to_csv(DATA_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"Erro no Motor: {e}")
        return False

def dashboard_performance_simples():
    st.header("📊 Raio-X de Performance")
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        
        # Interface de Injeção Manual (O que você pediu!)
        with st.expander("➕ Injetar Produto Manualmente"):
            col1, col2 = st.columns(2)
            p_nome = col1.text_input("Nome do Produto")
            p_link = col2.text_input("Cole o Link da Shopee aqui")
            p_nicho = st.selectbox("Nicho", ["Utilidades", "Cozinha", "Decoração", "Pets"])
            if st.button("🚀 Injetar Link Manual"):
                if p_nome and p_link:
                    aplicar_seo_viral(p_nome, p_link, p_nicho)
                    st.success("Produto injetado com sucesso!")
                    st.rerun()

        # Tabela de Monitoramento
        st.subheader("📅 Cronograma de Postagens")
        if "loja" not in df.columns: df["loja"] = "Shopee 🟠"
        
        colunas_ver = ["data", "horario_previsto", "loja", "produto", "status", "link_afiliado"]
        st.data_editor(
            df[colunas_ver].tail(20),
            column_config={
                "loja": st.column_config.TextColumn("Mercado"),
                "link_afiliado": st.column_config.LinkColumn("Link", display_text="Abrir 🛒")
            },
            disabled=["data", "loja"],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhum dado encontrado.")
