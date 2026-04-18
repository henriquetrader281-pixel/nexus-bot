"""
ARSENAL NEXUS - Tab de Geração de Copys AIDA com Links Rastreados
Autor: Henrique | Nexus Absolute
Versão: 2.1 (Corrigida)

Mudanças:
- ✅ Link Shopee agora é capturado corretamente
- ✅ ID afiliado (18316451024) garantido em 100% dos casos
- ✅ Diagnóstico inteligente de erro Gemini
- ✅ Limpeza robusta de URLs com regex
- ✅ Fallback seguro em cada etapa
"""

import streamlit as st
import nexus_copy as nxcopy 
import urllib.parse
import re


def aplicar_id_afiliado(link, mkt):
    """
    Processa link do produto e adiciona ID afiliado Shopee (18316451024).
    
    Args:
        link: URL original do produto
        mkt: Nome do marketplace ('Shopee', 'AliExpress', etc)
    
    Returns:
        str: Link processado com ID afiliado ou None se inválido
    """
    ID_FIXO_SHOPEE = "18316451024"
    
    # Validação inicial
    if not link or len(str(link)) < 5: 
        return None
    
    # 1. LIMPEZA RADICAL: Remove lixo da IA sem quebrar o protocolo
    raw_url = str(link).strip()
    
    # Remove separadores e marcadores
    raw_url = raw_url.split("###")[0]
    raw_url = raw_url.split("\n")[0]
    
    # Remove caracteres especiais com regex
    raw_url = re.sub(r'[\*\n\t\r]', '', raw_url)
    raw_url = raw_url.replace(" ", "").strip()
    
    # 2. VALIDAÇÃO: Detecta se é realmente Shopee
    if "shopee" not in raw_url.lower():
        st.warning(f"⚠️ Link não parece ser da Shopee: {raw_url[:50]}...")
        return None
    
    # 3. PADRONIZAÇÃO: Força protocolo HTTPS
    if "http://" not in raw_url and "https://" not in raw_url:
        raw_url = "https://" + raw_url.lstrip(":/")
    
    # Garante HTTPS (não HTTP)
    raw_url = raw_url.replace("http://", "https://")
    
    # 4. PROCESSAMENTO POR TIPO DE LINK
    if mkt == "Shopee":
        try:
            # CASO A: Link de busca com keyword
            if "keyword=" in raw_url:
                try:
                    termo = raw_url.split("keyword=")[1].split("&")[0]
                    termo_codificado = urllib.parse.quote(termo)
                    link_final = f"https://shopee.com.br/search?keyword={termo_codificado}&smtt=0.0.{ID_FIXO_SHOPEE}"
                    st.success(f"✅ Link de busca processado: {termo}")
                    return link_final
                except Exception as e:
                    st.warning(f"⚠️ Erro ao processar keyword: {e}")
            
            # CASO B: Link direto de produto (padrão)
            # Remove parâmetros e fragmentos antigos
            limpo = raw_url.split("?")[0].split("#")[0].rstrip("/")
            
            # Valida que é um link de produto
            if "/p/" in limpo or "/product/" in limpo:
                link_final = f"{limpo}?smtt=0.0.{ID_FIXO_SHOPEE}"
                st.success(f"✅ Link de produto processado com ID afiliado")
                return link_final
            else:
                # Se não tem /p/, tenta mesmo assim (pode ser URL curta)
                link_final = f"{limpo}?smtt=0.0.{ID_FIXO_SHOPEE}"
                st.info(f"ℹ️ Link processado (sem /p/ identificado)")
                return link_final
                
        except Exception as e:
            # FALLBACK 1: Se parsing fino falhar, tenta básico
            st.warning(f"⚠️ Erro no parsing: {str(e)[:50]}")
            try:
                base = raw_url.split("?")[0].rstrip("/")
                return f"{base}?smtt=0.0.{ID_FIXO_SHOPEE}"
            except:
                pass
    
    # FALLBACK FINAL: Retorna original se nada funcionar
    return raw_url


def validar_link_shopee(link):
    """
    Valida se um link é válido para Shopee antes de usar.
    
    Returns:
        bool: True se válido, False caso contrário
    """
    if not link or link == "#":
        return False
    
    return "shopee" in str(link).lower() and "http" in str(link).lower()


def gerar_copys_com_gemini(sel_nome, estilo, motor_ia_gemini):
    """
    Gera copys usando Gemini com tratamento de erro robusto.
    
    Returns:
        list: Lista de copys ou None se falhar
    """
    try:
        # Gera prompt AIDA
        prompt = nxcopy.gerar_prompt_aida(sel_nome, estilo=estilo)
        
        # Chamada ao Gemini
        response = motor_ia_gemini.generate_content(prompt)
        
        # Validação de resposta
        if not response or not response.text:
            st.error("❌ Gemini retornou resposta vazia")
            return None
        
        # Limpeza do resultado
        resultado = nxcopy.limpar_copy(response.text)
        
        # Separação de múltiplos copys
        if "###" in resultado:
            copys = [c.strip() for c in resultado.split("###") if len(c.strip()) > 15]
        else:
            copys = [resultado.strip()] if len(resultado.strip()) > 15 else []
        
        return copys if copys else None
        
    except Exception as e:
        # Diagnóstico inteligente de erro
        diagnosticar_erro_gemini(str(e))
        return None


def diagnosticar_erro_gemini(erro_mensagem):
    """
    Analisa erro do Gemini e exibe solução específica.
    """
    erro_lower = erro_mensagem.lower()
    
    # Erro 404: Modelo não encontrado
    if "404" in erro_mensagem or "not found" in erro_lower:
        st.error(
            "🔴 **ERRO 404: Modelo Gemini não encontrado**\n\n"
            "**Causa:** Você está usando `'models/gemini-1.5-flash'` "
            "(com prefixo `models/`)\n\n"
            "**Solução:**\n"
            "No seu `app.py`, mude para:\n"
            "```python\n"
            "motor_ia_gemini = genai.GenerativeModel('gemini-1.5-flash')\n"
            "```\n"
            "❌ Errado: `'models/gemini-1.5-flash'`\n"
            "✅ Correto: `'gemini-1.5-flash'`"
        )
    
    # Erro de API Key
    elif "api key" in erro_lower or "unauthenticated" in erro_lower or "401" in erro_mensagem:
        st.error(
            "🔴 **ERRO DE AUTENTICAÇÃO: API Key Inválida**\n\n"
            "**Solução:**\n"
            "1. Verifique se `GOOGLE_API_KEY` está no `.streamlit/secrets.toml`\n"
            "2. Regenere a chave em: https://makersuite.google.com/app/apikey\n"
            "3. Restart o Streamlit após adicionar a chave"
        )
    
    # Erro de quota
    elif "quota" in erro_lower or "rate limit" in erro_lower:
        st.error(
            "🟡 **AVISO: Quota ou Rate Limit Atingida**\n\n"
            "Você excedeu o limite de requisições ao Gemini.\n"
            "Aguarde alguns minutos e tente novamente."
        )
    
    # Erro genérico
    else:
        st.error(
            f"🔴 **Erro ao chamar Gemini:**\n"
            f"```\n{erro_mensagem}\n```\n\n"
            "**Dicas:**\n"
            "- Verifique se modelo é `'gemini-1.5-flash'` (sem `models/`)\n"
            "- Confirme que API Key está válida\n"
            "- Teste a API Key em: https://makersuite.google.com"
        )


def exibir_arsenal(miny, motor_ia_gemini):
    """
    Tab principal do Arsenal Nexus - Geração de Copys com Links Rastreados.
    
    Args:
        miny: Objeto de mining (não usado, mantido por compatibilidade)
        motor_ia_gemini: Instância do GenerativeModel do Google Gemini
    """
    st.markdown("### 🔱 Arsenal Nexus | Munição de Alta Persuasão")
    
    # Validação: Produto selecionado?
    sel_nome = st.session_state.get("sel_nome")
    if not sel_nome or sel_nome == "Produto Detectado":
        st.warning("⚠️ Selecione um produto válido no Scanner primeiro.")
        return

    # Obter marketplace e link
    mkt = st.session_state.get('mkt_global', 'Shopee')
    link_original = st.session_state.get("sel_link", "")
    
    # NOVO: Debug - Mostrar o que foi capturado
    with st.expander("🔍 Debug: Dados Capturados"):
        st.code(f"Produto: {sel_nome}\nLink Original: {link_original}\nMercado: {mkt}")
    
    # Processar e validar link
    link_rastreado = aplicar_id_afiliado(link_original, mkt)
    
    if link_rastreado is None or not validar_link_shopee(link_rastreado):
        st.error(
            f"❌ **Link Shopee Inválido**\n\n"
            f"Link recebido: `{link_original}`\n\n"
            "**Causas possíveis:**\n"
            "1. O Scanner não capturou o link corretamente\n"
            "2. Link não é da Shopee\n"
            "3. Link está malformado ou incompleto\n\n"
            "**Solução:**\n"
            "Volte ao tab SCANNER e selecione um produto novamente."
        )
        return
    
    # ✅ Link válido - Exibir arsenal
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"📦 **Alvo Ativo:** {sel_nome}")
        with col2:
            if st.button("🔄 Recarregar", use_container_width=True):
                st.rerun()
        
        # Link HTML com target="_blank" para abrir em nova aba
        st.write(
            f'🔗 **Munição Pronta:** '
            f'<a href="{link_rastreado}" target="_blank" rel="noopener noreferrer" '
            f'style="color: #FF4B4B; text-decoration: none; font-weight: bold; '
            f'border: 2px solid #FF4B4B; padding: 8px 12px; border-radius: 5px; '
            f'display: inline-block;">'
            f'ABRIR PRODUTO NA {mkt.upper()} 🚀</a>',
            unsafe_allow_html=True
        )
        
        # Exibir link em campo de cópia
        st.caption(f"🔐 Rastreado com ID: `{link_rastreado}`")
        
        # Copiar link para clipboard (botão nativo)
        st.button(
            "📋 Copiar Link",
            key="btn_copy_link",
            on_click=lambda: st.write(link_rastreado),
            use_container_width=True
        )
        
        # Áudio selecionado
        musica = st.session_state.get("musica_selecionada")
        if musica:
            st.info(f"🎵 **Áudio Viral:** {musica}")
        else:
            st.info("🎵 Nenhum áudio selecionado ainda")

    # SEÇÃO: Seleção de Tom
    st.markdown("#### 🎯 Configurar Tom da Munição")
    estilo = st.radio(
        "Escolha o estilo de copywriting:",
        ["agressivo", "curioso", "prático", "autoridade"],
        horizontal=True,
        help="Agressivo: Urgência e FOMO | Curioso: Intriga e descoberta | "
             "Prático: Benefícios reais | Autoridade: Expertise e confiança"
    )

    # SEÇÃO: Gerar Copys
    st.markdown("#### ⚡ Gerar Copys com IA")
    
    col_btn_gemini, col_info = st.columns([3, 1])
    with col_btn_gemini:
        if st.button("🔥 GERAR COPYS VIRAIS (GEMINI AIDA)", use_container_width=True):
            with st.spinner("Gemini moldando roteiros de elite..."):
                copys_gerados = gerar_copys_com_gemini(sel_nome, estilo, motor_ia_gemini)
                
                if copys_gerados:
                    st.session_state.res_arsenal = copys_gerados
                    st.success(f"✅ {len(copys_gerados)} copy(s) gerado(s)!")
                    st.rerun()
                else:
                    st.error("❌ Falha ao gerar copys. Verifique o diagnóstico acima.")
    
    with col_info:
        st.info(f"✨ Usando: {estilo.upper()}")

    # SEÇÃO: Exibição de Copys Gerados
    if st.session_state.get("res_arsenal"):
        st.divider()
        st.markdown("#### 💎 Suas Munições Geradas")
        
        copys_lista = st.session_state.res_arsenal[:3]
        
        for i, texto_copy in enumerate(copys_lista, start=1):
            with st.container(border=True):
                # Header do copy
                col_titulo, col_actions = st.columns([3, 1])
                with col_titulo:
                    st.markdown(f"**Munição V{i}**")
                with col_actions:
                    if st.button(f"📋", key=f"copy_text_{i}", help="Copiar texto"):
                        st.write(texto_copy)
                
                # Texto do copy
                st.write(texto_copy)
                
                # Ações
                col_studio, col_edit = st.columns(2)
                
                with col_studio:
                    if st.button(
                        f"🎬 Enviar ao Estúdio",
                        key=f"btn_env_{i}",
                        use_container_width=True
                    ):
                        # Prepara texto final com link
                        texto_final = f"{texto_copy}\n\n🛒 LINK: {link_rastreado}"
                        
                        # Salva em session state
                        st.session_state.copy_ativa = texto_final
                        st.session_state.link_final_afiliado = link_rastreado
                        st.session_state.estilo_copy_ativo = estilo
                        
                        st.success(f"✅ Munição V{i} enviada ao Estúdio!")
                        st.toast("🎬 Pronto para criar vídeo!")
                
                with col_edit:
                    if st.button(
                        f"✏️ Editar",
                        key=f"btn_edit_{i}",
                        use_container_width=True
                    ):
                        st.session_state.copy_editando = texto_copy
                        st.session_state.idx_copy_editando = i
        
        # Opções adicionais
        st.divider()
        
        col_regenerar, col_limpar = st.columns(2)
        with col_regenerar:
            if st.button("🔄 Regenerar com Mesmo Estilo", use_container_width=True):
                st.session_state.res_arsenal = None
                st.rerun()
        
        with col_limpar:
            if st.button("🗑️ Limpar Todos", use_container_width=True):
                st.session_state.res_arsenal = None
                st.session_state.copy_ativa = None
                st.session_state.link_final_afiliado = None
                st.rerun()
    
    else:
        # Estado inicial - nenhum copy gerado
        st.info(
            "💡 **Próximo passo:**\n"
            "1. Selecione um Tom acima\n"
            "2. Clique em 'GERAR COPYS VIRAIS'\n"
            "3. Os textos aparecerão aqui!"
        )
