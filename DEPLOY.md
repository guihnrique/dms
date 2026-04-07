# Deploy Guide - Render.com

Este guia explica como fazer o deploy da aplicação DMS no Render.com usando o banco de dados Neon PostgreSQL.

## Pré-requisitos

1. **Conta no Render.com**: Criar conta gratuita em [https://render.com](https://render.com)
2. **Conta no Neon**: Já configurado
3. **Repositório GitHub**: Código já está no GitHub

## Passos para Deploy

### 1. Preparar o Banco de Dados Neon

1. Acesse seu dashboard no Neon
2. Copie a **Connection String** do seu banco de dados
   - Deve estar no formato: `postgresql://user:password@host/database?sslmode=require`
3. Para o FastAPI, precisamos converter para formato asyncpg:
   ```
   postgresql+asyncpg://user:password@host/database?ssl=require
   ```

### 2. Deploy usando render.yaml (Recomendado)

#### Opção A: Deploy via Dashboard

1. **Acesse o Render Dashboard**
   - Vá para [https://dashboard.render.com](https://dashboard.render.com)
   - Clique em "New +" → "Blueprint"

2. **Conecte o Repositório**
   - Selecione seu repositório GitHub (guihnrique/dms)
   - O Render detectará automaticamente o arquivo `render.yaml`

3. **Configure as Variáveis de Ambiente**
   
   Para o **Backend (dms-api)**:
   - `DATABASE_URL`: Cole sua string de conexão Neon (formato asyncpg)
   - `JWT_SECRET`: Será gerado automaticamente (ou defina um personalizado)
   - `FRONTEND_URL`: Aguarde o deploy do frontend e cole a URL aqui
   
   Para o **Frontend (dms-frontend)**:
   - `VITE_API_URL`: Aguarde o deploy do backend e cole a URL aqui

4. **Deploy Inicial**
   - Clique em "Apply"
   - Aguarde o deploy de ambos os serviços (5-10 minutos)

5. **Atualizar URLs Cruzadas**
   - Após ambos os serviços estarem no ar, atualize:
     - `FRONTEND_URL` no backend com a URL do frontend
     - `VITE_API_URL` no frontend com a URL do backend
   - Os serviços serão automaticamente reconstruídos

#### Opção B: Deploy Manual (Separado)

Se preferir fazer deploy manual de cada serviço:

##### Backend API

1. No Dashboard do Render: **New + → Web Service**
2. Conecte seu repositório
3. Configure:
   - **Name**: `dms-api`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

4. **Environment Variables**:
   ```
   DATABASE_URL=postgresql+asyncpg://[sua-string-neon]
   JWT_SECRET=[gere-uma-chave-segura]
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_HOURS=24
   ENVIRONMENT=production
   FRONTEND_URL=[url-do-frontend-depois-do-deploy]
   ```

5. Clique em "Create Web Service"

##### Frontend

1. No Dashboard do Render: **New + → Static Site**
2. Conecte o mesmo repositório
3. Configure:
   - **Name**: `dms-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. **Environment Variables**:
   ```
   VITE_API_URL=[url-do-backend-api]
   ```

5. Clique em "Create Static Site"

### 3. Executar Migrações do Banco de Dados

Após o deploy do backend, você precisa executar as migrações:

1. Acesse o **Shell** do seu serviço backend no Render:
   - Dashboard → dms-api → Shell (no menu lateral)

2. Execute os scripts de migração:
   ```bash
   cd backend
   python scripts/run_migrations.py
   ```

3. (Opcional) Popular o banco com dados de exemplo:
   ```bash
   python scripts/quick_seed.py
   ```

### 4. Testar a Aplicação

1. Acesse a URL do frontend fornecida pelo Render
2. Teste o registro e login
3. Verifique se as funcionalidades estão funcionando

## URLs Finais

Após o deploy, suas URLs serão:
- **Frontend**: `https://dms-frontend.onrender.com`
- **Backend API**: `https://dms-api.onrender.com`
- **Documentação API**: `https://dms-api.onrender.com/api/docs`

## Limitações do Plano Gratuito

⚠️ **Importante sobre o plano gratuito do Render:**

- Os serviços entram em **sleep mode** após 15 minutos de inatividade
- O primeiro acesso após o sleep pode demorar 30-50 segundos
- 750 horas gratuitas por mês (suficiente para 1 serviço 24/7)
- Para manter 2 serviços (backend + frontend), considere:
  - Usar apenas um serviço que serve ambos (requer configuração diferente)
  - Ou aceitar que backend pode dormir quando não usado

## Alternativas de Hospedagem Gratuita

Se quiser explorar outras opções:

### Railway.app
- $5 de crédito grátis por mês
- Similar ao Render, fácil de usar
- Suporta PostgreSQL externo

### Fly.io
- Tier gratuito generoso
- Boa performance global
- Requer configuração via CLI

### Vercel (apenas Frontend) + Render (Backend)
- Vercel é excelente para React
- Deploy frontend no Vercel, backend no Render

## Troubleshooting

### Backend não conecta ao banco
- Verifique se a string de conexão está no formato `postgresql+asyncpg://`
- Confirme que tem `?ssl=require` no final
- Verifique se o IP do Render está permitido no Neon

### CORS Errors
- Verifique se `FRONTEND_URL` no backend está correto
- Deve incluir `https://` e não terminar com `/`
- Exemplo: `https://dms-frontend.onrender.com`

### Frontend não conecta ao backend
- Verifique `VITE_API_URL` no frontend
- Teste a API diretamente: `https://dms-api.onrender.com/health`

### Serviço em Sleep Mode
- Primeira requisição demora mais (normal)
- Considere usar um serviço de "ping" para manter ativo
- Ou aceitar o delay do plano gratuito

## Monitoramento

No Render Dashboard você pode:
- Ver logs em tempo real
- Monitorar uso de recursos
- Configurar alertas
- Ver métricas de performance

## Próximos Passos

Após o deploy bem-sucedido:
1. Configure um domínio customizado (opcional)
2. Configure SSL (automático no Render)
3. Configure backup do banco de dados no Neon
4. Configure monitoring e alertas
5. Documente as credenciais de admin
