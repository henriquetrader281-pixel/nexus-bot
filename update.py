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
    # 20 Horários para cobrir a mineração estendida
    horarios = [
        "08:30", "09:15", "10:00", "11:15", "12:00", "12:45", "14:00", "15:30", 
        "17:00", "17:30", "18:15", "18:50", "19:30", "20:10", "20:45", "21:30", 
        "22:00", "22:45", "23:15", "00:00"
    ]

    # --- TRAVA E IDENTIFICAÇÃO DA LOJA ---
    is_shopee = "shopee.com.br" in link_base or "shope.ee" in link_base
    loja_label = "Shopee 🟠" if is_shopee else "Outro ⚪"

    if not is_shopee:
        st.error(f"❌ Erro: O produto '{produto}' não é da Shopee. Use apenas links da Shopee Brasil.")
        return False

    try:
        aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
        
        if not os.path.exists(DATA_PATH):
            pd.DataFrame(columns=["data", "loja", "produto", "link_afiliado", "copy_funil", "roteiro", "horario_previsto", "status"]).to_csv(DATA_PATH, index=False)
        
        df = pd.read_csv(DATA_PATH)
        novas = []

        # IA Gerando 20 roteiros para você ter seleção
        prompt_roteiros = f"""
        Aja como um criador de conteúdo do TikTok. 
        Crie 20 roteiros ultra-curtos (3 cenas cada) para o produto {produto} no nicho {nicho}.
        REGRAS: Sem negrito (**), sem a palavra 'PRODUTO:', separe os 20 apenas por '###'.
        """
        res_raw = gerar_ia_interna(prompt_roteiros)
        res_roteiros = res_raw.split("###")

        # Limpeza do nome do produto
        nome_limpo = produto.replace("*", "").replace("PRODUTO:", "").replace("1.", "").strip()

        # Geramos 20 variações para você selecionar as melhores no monitor
        for i in range(min(20, len(res_roteiros))):
            link_track = f"{link_base}?sp_atk=nexus&utm_source=affiliate&utm_campaign={aff_id}&sub_id=V{i+1}"
            
            legenda = f"{random.choice(ganchos)} {nome_limpo}! ✨ {' '.join(random.sample(hashtags, 3))}"
            roteiro_final = res_roteiros[i].strip().replace("*", "")

            novas.append({
                "data": datetime.now().strftime("%d/%m"),
                "loja": loja_label,
                "produto": f"{nome_limpo} [V{i+1}]",
                "link_afiliado": link_track,
                "copy_funil": legenda,
                "roteiro": roteiro_final,
                "horario_previsto": horarios[i % len(horarios)],
                "status": "PRONTO"
            })
        
        pd.concat([df, pd.DataFrame(novas)], ignore_index=True).to_csv(DATA_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"Erro no Motor de Escala: {e}")
        return False

def dashboard_performance_simples():
    st.header("📊 Raio-X de Performance (Monitor Nexus)")
    if os.path.exists(DATA_PATH):
        try:
            df = pd.read_csv(DATA_PATH)
            
            # Garante que a coluna 'loja' exista para itens legados
            if "loja" not in df.columns:
                df["loja"] = "Shopee 🟠"

            # Métricas
            c1, c2 = st.columns(2)
            c1.metric("📦 Na Fila (PRONTO)", len(df[df["status"]=="PRONTO"]))
            c2.metric("✅ Postados (ENVIADO)", len(df[df["status"]=="ENVIADO"]))

            st.subheader("📅 Cronograma de Postagens Diárias")
            
            # Ordem visual estratégica
            colunas_monitor = ["data", "horario_previsto", "loja", "produto", "status", "link_afiliado", "copy_funil"]
            
            st.data_editor(
                df[colunas_monitor].tail(40), # Mostra as últimas 40 para você selecionar
                column_config={
                    "loja": st.column_config.TextColumn("Fonte", width="small"),
                    "link_afiliado": st.column_config.LinkColumn("Link de Venda", display_text="Abrir Produto 🛒"),
                    "status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["PRONTO", "ENVIADO", "CANCELADO"],
                        help="Mude para CANCELADO se não quiser postar este item"
                    )
                },
                disabled=["data", "horario_previsto", "loja"], 
                use_container_width=True,
                hide_index=True
            )
        except Exception as e:
            st.error(f"Erro ao carregar monitor: {e}")
    else:
        st.info("Aguardando a primeira injeção de produtos...")
