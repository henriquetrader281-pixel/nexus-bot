import pandas as pd
import requests
import time
from datetime import datetime
import os

DATA_PATH = "dataset_nexus.csv"
WEBHOOK = "SEU_WEBHOOK_AQUI" 

def verificar_fila():
    if not os.path.exists(DATA_PATH): return
    df = pd.read_csv(DATA_PATH)
    agora = datetime.now().strftime("%H:%M")
    hoje = datetime.now().strftime("%d/%m")
    
    fila = df[(df["status"] == "PRONTO") & (df["data"] == hoje)]
    
    for idx, row in fila.iterrows():
        if agora >= str(row['horario_previsto']):
            print(f"🚀 Disparando Variação: {row['produto']} às {agora}")
            payload = {
                "content": f"🔥 {row['copy_funil']}\n\n🛒 Link: {row['link_afiliado']}",
                "metadata": {"ref": row['produto'], "hora": row['horario_previsto']}
            }
            try:
                if requests.post(WEBHOOK, json=payload, timeout=20).status_code < 300:
                    df.at[idx, "status"] = "ENVIADO"
                    df.to_csv(DATA_PATH, index=False)
            except: print("Erro na conexão com o Webhook.")

if __name__ == "__main__":
    print("🔱 Nexus Scheduler V2 Ativo | Monitorando Horários de Pico...")
    while True:
        verificar_fila()
        time.sleep(60) # Verifica a cada minuto
