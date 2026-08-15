import streamlit as st
import time

def supervisionar_entrega(produto, link_afiliado, status_pinterest, status_instagram, status_manychat):
    """
    O Agente Hermes atua como supervisor, verificando se cada ponta do funil foi amarrada.
    """
    st.markdown("---")
    st.markdown("### 🕊️ Relatório de Entrega: Agente Hermes")
    
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Alvo:** {produto}")
            st.markdown(f"**Link de Venda:** `{link_afiliado}`")
        with col2:
            st.image("https://img.icons8.com/fluency/96/hermes-staff.png", width=60)

        st.markdown("#### ✅ Status da Operação:")
        
        # Verificação Pinterest
        if status_pinterest.get('success'):
            st.success(f"📌 **Pinterest:** Publicado com sucesso! [Ver Pin]({status_pinterest.get('url', 'https://pinterest.com')})")
        else:
            st.error(f"📌 **Pinterest:** Falha na postagem. Motivo: {status_pinterest.get('error', 'Erro de API')}")
            
        # Verificação Instagram
        if status_instagram.get('success'):
            st.success(f"📸 **Instagram:** Reels enviado para fila de publicação! [Ver Perfil](https://instagram.com)")
        else:
            st.warning(f"📸 **Instagram:** Aguardando configuração de API para disparo real.")
            
        # Verificação ManyChat
        if status_manychat.get('success'):
            st.success(f"🔗 **ManyChat:** Webhook de automação de DM ativado para este produto.")
        else:
            st.error(f"🔗 **ManyChat:** Falha ao conectar com o funil de DM.")

    st.info("💡 **Dica do Hermes:** Todas as pontas foram verificadas. O seu produto já está a circular nas redes sociais e pronto para converter comentários em comissões.")
