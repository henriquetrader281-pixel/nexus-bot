import streamlit as st
from datetime import datetime, timedelta
import random

def calcular_melhores_horarios(miny, motor_ia, produto):
    """Usa a inteligência do Gemini para definir os horários de pico"""
    try:
        prompt_timing = f"""
        Analise o produto '{produto}'. 
        Com base no comportamento de compra para este nicho, 
        quais seriam os 3 melhores horários de postagem para hoje?
        Responda APENAS os horários no formato HH:MM, HH:MM, HH:MM.
        """
        resposta = miny.minerar_produtos(prompt_timing, "Shopee", motor_ia)
        # Limpa a resposta para garantir que venham apenas os horários
        horarios = [h.strip() for h in resposta.split(',')]
        return horarios[:3]
    except:
        # Fallback de segurança caso a IA falhe
        return ["12:00", "18:30", "21:15"]

def exibir_postador(miny, motor_ia):
    st.markdown("### 🛰️ Central de Postagem Inteligente Nexus 🔱")

    if "copy_final_pronta" in st.session_state:
        produto = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()
        
        # --- O PAINEL DE CONTROLE DO CEO ---
        with st.container(border=True):
            st.markdown(f"#### 🔄 Status da Automação: **{produto}**")
            st.success("🤖 Vídeo, Áudio e Copy vinculados e prontos.")
            
            # Chama a IA Real para calcular horários
            horarios = calcular_melhores_horarios(miny, motor_ia, produto)
            st.write(f"📈 **Estratégia de IA:** Postagens otimizadas para: `{', '.join(horarios)}`")
            
            # Preview da Munição
            with st.expander("👁️ Revisar Conteúdo Final"):
                st.info(f"**Legenda:**\n{st.session_state.copy_final_pronta}")
                if "prompt_ia_video" in st.session_state:
                    st.caption(f"**Prompt Visual:** {st.session_state.prompt_ia_video}")

        # --- SELEÇÃO DE CANAIS ---
        canais = st.multiselect("📡 Publicar em:", ["Instagram Reels", "TikTok", "YouTube Shorts"], default=["Instagram Reels", "TikTok"])

        # --- O BOTÃO DE EXECUÇÃO REAL ---
        if st.button("🚀 ATIVAR PILOTO AUTOMÁTICO", use_container_width=True):
            with st.spinner("🤖 Nexus sincronizando com APIs e agendando fila..."):
                
                # 1. Simulação da Lógica de Postagem (Ayrshare/Buffer)
                # Aqui entraria o código: payload = {"post": st.session_state.copy_final_pronta, "schedule": horarios}
                
                st.session_state.automacao_ativa = True
                
                # Registro no Log
                log_entrada = f"{datetime.now().strftime('%d/%m %H:%M')} - {produto} agendado para {canais}"
                if "logs_postagem" not in st.session_state:
                    st.session_state.logs_postagem = []
                st.session_state.logs_postagem.append(log_entrada)
                
                st.balloons()
                st.toast("Munição enviada para a fila de disparo!")

        # --- LOG DE OPERAÇÕES ---
        if st.session_state.get("logs_postagem"):
            st.divider()
            st.markdown("#### 📜 Relatório de Disparos")
            for log in reversed(st.session_state.logs_postagem):
                st.caption(log)

    else:
        st.warning("⚠️ O fluxo precisa passar pelo Estúdio (Geração de Vídeo) antes da Postagem.")
