# Configurar a senha do Nexus Master

O Nexus não tem uma senha padrão no código. O segredo é definido pelo proprietário no ambiente de execução.

## Streamlit Community Cloud

1. Entre em https://share.streamlit.io/ e abra o app Nexus Master.
2. Abra **Settings → Secrets**.
3. Adicione uma senha forte com este formato:

   NEXUS_PASSWORD = "sua-senha-forte"

4. Salve e recarregue o app. Use exatamente o valor que você colocou entre aspas como senha de login.

Se já existe uma configuração NEXUS_PASSWORD, mas você não lembra a senha, substitua o valor por uma nova senha nesse mesmo local e salve.

## Execução local

Crie o arquivo .streamlit/secrets.toml na pasta do projeto e coloque nele:

   NEXUS_PASSWORD = "sua-senha-forte"

Não publique secrets.toml no GitHub nem envie a senha em mensagens ou issues.

## Importante

- Não existe uma senha universal ou recuperável no código.
- Se você não tiver acesso às configurações do app no Streamlit Cloud, o proprietário/administrador do app precisará alterar o segredo.
