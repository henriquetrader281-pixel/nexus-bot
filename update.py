import pandas as pd
import urllib.parse
from datetime import datetime
import streamlit as st
import random
import os
from groq import Groq

DATA_PATH = "dataset_nexus.csv"

# --- FUNÇÃO DE IA INTEGRADA NO UPDATE ---
def gerar_ia_interna(prompt):
    try:
        # Puxa a chave direto dos secrets do Streamlit
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
    horarios = ["11:15", "12:45", "17:30", "18:50", "20:10", "21:30", "22:45", "08:30", "15:00", "19:55"]

    # --- TRAVA DE SEGURANÇA: SÓ ACEITA SHOPEE ---
    if "shopee.com.br" not in link_base and "shope.ee" not in link_base:
        st.error(f"❌ Erro: O produto '{produto}' não é da Shopee. Use apenas links da Shopee Brasil.")
        return False

    try:
        aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
        
        # Garante que o arquivo existe
        if not os.path.exists(DATA_PATH):
            pd.DataFrame(columns=["data", "produto", "link_afiliado", "copy_funil", "roteiro", "horario_previsto", "status"]).to_csv(DATA_PATH, index=False)
        
        df = pd.read_csv(DATA_PATH)
        novas = []

        # --- IA COM PROMPT HUMANIZADO ---
        prompt_roteiros = f"""
        Aja como um criador de conteúdo do TikTok. 
        Crie 10 roteiros curtos (3 cenas cada) para o produto {produto} no nicho {nicho}.
        IMPORTANTE: Não use negrito (**), não use a palavra 'PRODUTO:' e separe os 10 roteiros apenas por '###'.
        """
        res_raw = gerar_ia_interna(prompt_roteiros)
        res_roteiros = res_raw.split("###")

        # --- LIMPEZA DE TEXTO (Anti-Robô) ---
        nome_limpo = produto.replace("*", "").replace("PRODUTO:", "").replace("1.", "").replace("2.", "").strip()

        for i in range(10):
            # Link de Rastreio Direto (Sem erro de API)
            link_track = f"{link_base}?sp_atk=nexus&utm_source=affiliate&utm_campaign={aff_id}&sub_id=V{i+1}"
            
            # Legenda Viral
            gancho = random.choice(ganchos)
            tags = ' '.join(random.sample(hashtags, 3))
            legenda_final = f"{gancho} {nome_limpo}! ✨ {tags}"
            
            # Roteiro Limpo
            roteiro_raw = res_roteiros[i].strip() if i < len(res_roteiros) else "Cena 1: Gancho | Cena 2: Uso | Cena 3: Link"
            roteiro_final = roteiro_raw.replace("*", "")

            novas.append({
                "data": datetime.now().strftime("%d/%m"),
                "produto": f"{nome_limpo} [V{i+1}]",
                "link_afiliado": link_track,
                "copy_funil": legenda_final,
                "roteiro": roteiro_final,
                "horario_previsto": horarios[i],
                "status": "PRONTO"
            })
        
        # Salva as novas variações no CSV
        df_final = pd.concat([df, pd.DataFrame(novas)], ignore_index=True)
        df_final.to_csv(DATA_PATH, index=False)
        return True

    except Exception as e:
        st.error(f"Erro no Motor de Escala: {e}")
        return False

def dashboard_performance_simples():
    st.header("📊 Raio-X de Performance")
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        
        # Métricas rápidas
        c1, c2 = st.columns(2)
        c1.metric("📦 Na Fila (PRONTO)", len(df[df["status"]=="PRONTO"]))
        c2.metric("✅ Postados (ENVIADO)", len(df[df["status"]=="ENVIADO"]))

        st.subheader("📅 Cronograma de Postagens Diárias")
        
        # Colunas visíveis com o Link de Venda
        colunas_visiveis = ["data", "horario_previsto", "produto", "link_afiliado", "status", "copy_funil", "roteiro"]
        
        # TABELA COM LINK CLICÁVEL
        st.data_editor(
            df[colunas_visiveis].tail(20),
            column_config={
                "link_afiliado": st.column_config.LinkColumn(
                    "Link de Venda",
                    display_text="Abrir Produto 🛒"
                ),
            },
            disabled=True,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Aguardando a primeira injeção de produtos...")
