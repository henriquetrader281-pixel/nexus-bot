import pandas as pd
from datetime import datetime

def salvar_agendamento(produto, copy, link):
    try:
        df = pd.read_csv("nexus_master_data.csv")
        novo_dado = {
            "data": datetime.now().strftime("%d/%m/%Y"),
            "produto": produto,
            "status": "AGENDADO",
            "copy": copy
        }
        df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
        df.to_csv("nexus_master_data.csv", index=False)
        return "✅ Gravado no Nexus Master Data!"
    except Exception as e:
        return f"❌ Erro ao agendar: {e}"
