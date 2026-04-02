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
    
    fila = df[df["status"] == "PRONTO"]
    for idx, row in fila.iterrows():
        if agora >= str(row['horario_previsto']):
            print(f"🚀 Disparando SEO: {row['produto']}")
            payload = {"text": f"{row['copy_funil']}\n\n🛒 Link: {row['link_afiliado']}"}
            try:
                if requests.post(WEBHOOK, json=payload, timeout=20).status_code < 300:
                    df.at[idx, "status"] = "ENVIADO"
                    df.to_csv(DATA_PATH, index=False)
            except: print("Erro no disparo.")

if __name__ == "__main__":
    print("🔱 Nexus Scheduler Ativo...")
    while True:
        verificar_fila()
        time.sleep(60)
