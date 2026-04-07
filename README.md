# DMS - Digital Music Store 🎵

Uma plataforma moderna e imersiva de música digital com UI glassmorphism, recomendações personalizadas e gerenciamento completo de catálogo musical.

> **✨ Aplicação em Produção:**
> - 🌐 **Frontend**: [https://dms-frontend-lhlb.onrender.com](https://dms-frontend-lhlb.onrender.com)
> - ⚙️ **Backend API**: [https://dms-7iuv.onrender.com](https://dms-7iuv.onrender.com)
> - 📚 **API Docs**: [https://dms-7iuv.onrender.com/api/docs](https://dms-7iuv.onrender.com/api/docs)

## 🎯 Funcionalidades

### Backend API
- 🔐 **Autenticação** - JWT com cookies seguros (HttpOnly, Secure, SameSite=None)
- 🎵 **Catálogo Musical** - Artistas, Álbuns, Músicas com soft-delete
- 📝 **Playlists** - Criar, compartilhar e reordenar playlists
- ⭐ **Reviews & Avaliações** - Avaliar músicas com votação e moderação
- 🔍 **Busca Multi-Entidade** - Busca ranqueada por relevância com filtros
- 🎯 **Recomendações Personalizadas** - Sistema de recomendação baseado em preferências
- ❤️ **Favoritos** - Sistema completo de favoritos para músicas, álbuns e artistas

### Frontend React
- 🎨 **Neon Groove Design System** - UI glassmorphism com gradientes neon
- 🧩 **Biblioteca de Componentes** - Componentes reutilizáveis (Button, Card, Input, Icon, Navigation)
- 📱 **Design Responsivo** - Mobile-first, acessível (WCAG AA)
- ⚡ **Performance** - Vite + React 18 + TypeScript
- 🖼️ **Imagens Dinâmicas** - Integração com Picsum Photos para placeholders

## 🏗️ Estrutura do Projeto

```
DMS/
├── backend/          # FastAPI backend com PostgreSQL
│   ├── app/
│   │   ├── models/        # Modelos SQLAlchemy
│   │   ├── schemas/       # Schemas Pydantic
│   │   ├── repositories/  # Camada de acesso a dados
│   │   ├── services/      # Lógica de negócio
│   │   ├── routers/       # Endpoints da API
│   │   └── middleware/    # Middleware (CORS, rate limit)
│   ├── migrations/        # Migrações SQL
│   └── scripts/           # Scripts utilitários
├── frontend/         # React + TypeScript frontend com Vite
│   └── src/
│       ├── components/    # Componentes React
│       ├── pages/         # Páginas
│       ├── api/           # Cliente API
│       └── context/       # Context providers
└── .sdd/            # Spec-Driven Development specifications
```

## 🚀 Deploy em Produção

### Stack de Produção
- **Frontend**: Render.com (Static Site)
- **Backend**: Render.com (Web Service - Python 3.11)
- **Database**: Neon PostgreSQL (Serverless)
- **SSL**: Automático via Cloudflare

### URLs em Produção
- **Aplicação**: https://dms-frontend-lhlb.onrender.com
- **API**: https://dms-7iuv.onrender.com
- **Documentação**: https://dms-7iuv.onrender.com/api/docs

### Variáveis de Ambiente (Produção)

**Backend:**
```env
DATABASE_URL=postgresql+asyncpg://[user]:[pass]@[host]/[db]?ssl=require
JWT_SECRET=[gerado automaticamente]
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
ENVIRONMENT=production
FRONTEND_URL=https://dms-frontend-lhlb.onrender.com
```

**Frontend:**
```env
VITE_API_URL=https://dms-7iuv.onrender.com
```

### Fazer Novo Deploy

Para fazer deploy de novas alterações:

1. **Commit e Push** para o GitHub:
   ```bash
   git add .
   git commit -m "Sua mensagem"
   git push origin main
   ```

2. **Deploy Automático**: Render detecta automaticamente e faz redeploy (2-3 minutos)

Para instruções completas de deploy inicial, veja [DEPLOY.md](DEPLOY.md).

## 💻 Desenvolvimento Local

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL (ou usar Neon)

### Backend Setup

```bash
cd backend

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# Executar migrações
python scripts/run_migrations.py

# (Opcional) Popular banco com dados de exemplo
python scripts/quick_seed.py

# Iniciar servidor
uvicorn app.main:app --reload
```

Backend rodando em: `http://localhost:8000`  
API Docs: `http://localhost:8000/api/docs`

### Frontend Setup

```bash
cd frontend

# Instalar dependências
npm install

# Configurar API URL
echo "VITE_API_URL=http://localhost:8000" > .env

# Iniciar servidor de desenvolvimento
npm run dev
```

Frontend rodando em: `http://localhost:5173`

## 📡 Endpoints da API

### Autenticação
- `POST /api/v1/auth/register` - Criar conta
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Usuário atual

### Catálogo Musical
- `GET /api/v1/artists` - Listar artistas
- `GET /api/v1/albums` - Listar álbuns
- `GET /api/v1/songs` - Listar músicas (filtros: album_id, artist_id)

### Playlists
- `GET /playlists/me` - Minhas playlists
- `POST /playlists` - Criar playlist
- `POST /playlists/{id}/songs` - Adicionar música
- `DELETE /playlists/{id}/songs/{song_id}` - Remover música

### Reviews & Avaliações
- `GET /reviews/song/{id}` - Reviews de uma música
- `POST /reviews` - Criar/atualizar review
- `POST /reviews/{id}/vote` - Votar em review

### Favoritos
- `POST /favorites/songs/{id}` - Favoritar música
- `DELETE /favorites/songs/{id}` - Desfavoritar música
- `GET /favorites/songs` - Listar músicas favoritas
- `POST /favorites/albums/{id}` - Favoritar álbum
- `POST /favorites/artists/{id}` - Favoritar artista

### Busca & Recomendações
- `GET /search?q={query}` - Busca multi-entidade
- `GET /recommendations` - Recomendações personalizadas
- `POST /recommendations/feedback` - Feedback de recomendação

[Documentação completa da API](https://dms-7iuv.onrender.com/api/docs)

## 🗄️ Schema do Banco de Dados

### Tabelas Principais
- `users` - Contas de usuário com RBAC
- `artists` - Artistas (nome, país, foto)
- `albums` - Álbuns (título, ano, gênero, cover art)
- `songs` - Músicas (título, duração, gênero)
- `playlists` - Playlists dos usuários
- `playlist_songs` - Relacionamento playlist-música
- `reviews` - Avaliações de músicas
- `review_votes` - Votos em reviews
- `favorites` - Sistema de favoritos polimórfico
- `search_logs` - Analytics de busca
- `recommendation_feedback` - Tracking de recomendações

## 🛠️ Stack Tecnológica

### Backend
- **FastAPI** - Framework web assíncrono moderno
- **SQLAlchemy 2.0** - ORM assíncrono
- **PostgreSQL** - Banco de dados (Neon serverless)
- **Pydantic 2.x** - Validação de dados
- **JWT** - Autenticação
- **AsyncPG** - Driver PostgreSQL assíncrono
- **Bcrypt** - Hash de senhas

### Frontend
- **React 18** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool
- **Tailwind CSS** - Framework CSS
- **React Router** - Roteamento
- **Material Symbols** - Sistema de ícones

### Infraestrutura
- **Render.com** - Hospedagem (backend + frontend)
- **Neon** - PostgreSQL serverless
- **Cloudflare** - CDN e SSL
- **GitHub** - Versionamento e CI/CD

## 🧪 Testes

```bash
# Testes do backend
cd backend
source venv/bin/activate
pytest tests/ -v
pytest --cov=app tests/  # Com cobertura

# Testes do frontend
cd frontend
npm run test
npm run test:coverage
```

## 🏛️ Arquitetura

### Backend (Clean Architecture)
```
Routes → Services → Repositories → Models
```

- **Routes** - Endpoints HTTP com injeção de dependências
- **Services** - Lógica de negócio
- **Repositories** - Acesso a dados com sessões async
- **Models** - Modelos ORM SQLAlchemy

### Frontend (Component-Based)
```
Pages → Components → API Services → Backend
```

- **Pages** - Componentes de nível de rota
- **Components** - Componentes UI reutilizáveis
- **API Services** - Comunicação tipada com backend
- **Context** - Estado global (autenticação)

## ⚡ Performance

- Tempo de resposta da busca: **<300ms** (100k registros)
- Recomendações: **<1s** com fallback de timeout
- Database: **Row-level locking** para operações concorrentes
- Frontend: **Lazy loading** de rotas e componentes

## 🔒 Segurança

- **JWT Cookies** - HttpOnly, Secure, SameSite=None (cross-origin)
- **Rate Limiting** - 100 req/min (autenticado), 20 req/min (guest)
- **CORS** - Origens explícitas configuradas
- **Hash de Senhas** - Bcrypt com salt
- **Validação** - Pydantic para validação de entrada
- **SQL Injection** - Prevenido por SQLAlchemy ORM

## 🤝 Contribuindo

Este projeto segue **Spec-Driven Development (SDD)**:

1. Requirements (padrão EARS)
2. Design (arquitetura + fluxo de dados)
3. Tasks (TDD com Red-Green-Refactor)
4. Implementation

Veja o diretório `.sdd/` para especificações.

## 📄 Licença

MIT

## 👥 Autores

- **Guilherme Ferreira** - [@guihnrique](https://github.com/guihnrique)

## ✨ Status

✅ **Backend**: 100% completo (todas specs implementadas)  
✅ **Frontend**: 100% completo (design system + páginas)  
✅ **Database**: Todas migrações executadas  
✅ **Deploy**: Em produção no Render + Neon  
✅ **CI/CD**: Deploy automático via GitHub push

---

**Built with** ❤️ **using Claude Code and Spec-Driven Development**
