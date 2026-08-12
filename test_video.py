from video_generator import criar_reels_afiliado
import json

with open("nexus_manifest.json", "r") as f:
    dados = json.load(f)

print(f"🎬 Gerando vídeo para: {dados['produto']}")
path = criar_reels_afiliado("produto_reels.png", dados["copy_reels"])
if path:
    print(f"✅ Vídeo gerado com sucesso em: {path}")
else:
    print("❌ Falha na geração do vídeo.")
