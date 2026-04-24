if st.button("📊 SINCRONIZAR TENDÊNCIAS GLOBAIS", use_container_width=True):
        if not motor_ia:
            st.error("❌ Motor IA não detetado. Reinicie o sistema no Painel Nexus.")
        else:
            with st.spinner("IA Nexus fundindo dados das redes sociais..."):
                try:
                    hoje = datetime.now().strftime("%d/%m/%Y")
                    prompt = f"""
                    Analise tendências virais de HOJE ({hoje}) no TikTok e Reels Brasil. 
                    Retorne APENAS um JSON puro (sem markdown) com esta estrutura:
                    {{"trends": [
                        {{"musica": "nome", "razao": "por que é trend", "aida_hook": "gancho viral", "score": 95}},
                        {{"musica": "nome2", "razao": "...", "aida_hook": "...", "score": 90}}
                    ]}}
                    """
                    
                    # --- LÓGICA HÍBRIDA (GROQ OU GEMINI) ---
                    if hasattr(motor_ia, 'chat'): # Se for Groq
                        chat_completion = motor_ia.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.3-70b-versatile", # Ou o modelo que você usa
                            response_format={"type": "json_object"}
                        )
                        res_text = chat_completion.choices[0].message.content
                    else: # Se for Gemini
                        response = motor_ia.generate_content(prompt)
                        res_text = response.text.replace('```json', '').replace('```', '').strip()
                    
                    res = json.loads(res_text)
                    
                    if res:
                        st.session_state.cache_trends = res["trends"]
                        st.success("Dados Elite atualizados!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Erro ao fundir tendências: {e}")
