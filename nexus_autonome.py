import os
import time
import requests
from datetime import datetime

def executar_ciclo_autonomo():
    print("🔱 [Nexus Bot] A iniciar ciclo autónomo de descoberta de dores e oferta...")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openai_base_url = os.environ.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL") or os.environ.get("WEBHOOK_URL")
    
    resposta_ia = ""
    
    prompt_dor = """
    Analise o comportamento atual do consumidor online e redes sociais. 
    Identifique 1 dor, problema ou necessidade urgente que as pessoas estão a enfrentar atualmente no nicho de casa, produtividade ou eletrónicos.
    Retorne estritamente no formato:
    DOR: [descrição da dor]
    NICHO: [nicho]
    PRODUTO_SOLUCAO: [nome do produto físico que resolve esta dor]
    COPY_OFERTA: [uma copy persuasiva de 2 linhas focada na dor, com chamada para ação e espaço para link]
    """

    if openai_api_key:
        try:
            from openai import OpenAI
            client_kwargs = {"api_key": openai_api_key}
            if openai_base_url:
                client_kwargs["base_url"] = openai_base_url
            client = OpenAI(**client_kwargs)
            chat = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Você é um analista de mercado e especialista em copywriting de conversão."},
                    {"role": "user", "content": prompt_dor}
                ],
                model="gemini-3-flash-preview",
                temperature=0.7
            )
            resposta_ia = chat.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Erro com OpenAI/Proxy: {e}")

    if not resposta_ia:
        print("❌ ERRO: Nenhuma IA válida conseguiu responder.")
        return

    print("💡 [Nexus Bot] Dor e solução detetadas com sucesso pela IA:")
    print(resposta_ia)
    
    id_afiliado = "18316451024"
    link_afiliado = f"https://shopee.com.br/universal-link/search?smtt=0.0.{id_afiliado}&keyword=produto"
    
    mensagem_final = f"🚨 **RADAR DE NECESSIDADES NEXUS-BOT** 🚨\n\n{resposta_ia}\n\n🛒 **Link Direto de Oferta:** {link_afiliado}"
    
    if webhook_url and webhook_url != "SEU_WEBHOOK_AQUI":
        payload = {"content": mensagem_final}
        try:
            resp = requests.post(webhook_url, json=payload, timeout=20)
            if resp.status_code < 300:
                print("✅ [Nexus Bot] Oferta enviada com sucesso para o webhook!")
            else:
                print(f"⚠️ [Nexus Bot] Falha ao enviar para o webhook. Status: {resp.status_code}")
        except Exception as e:
            print(f"⚠️ Erro ao enviar webhook: {e}")
    else:
        print("ℹ️ [Nexus Bot] Nenhum webhook configurado. A executar em modo de simulação/local com sucesso.")
        
    return resposta_ia

if __name__ == "__main__":
    executar_ciclo_autonomo()
