# Database Seeding Scripts

Este diretório contém scripts para popular o banco de dados com dados reais de música.

## 🎵 seed_real_data.py

Script principal que usa a **MusicBrainz API** (gratuita e sem necessidade de autenticação) para popular o banco com dados reais.

### Artistas incluídos:

**Rock Internacional:**
- AC/DC, Metallica, Pink Floyd, Led Zeppelin
- The Beatles, Queen, Nirvana, Radiohead
- Arctic Monkeys, Red Hot Chili Peppers
- The Rolling Stones, Black Sabbath

**Rock/MPB Brasileiro:**
- Legião Urbana, Cazuza, Titãs
- Capital Inicial, Os Paralamas do Sucesso
- Chico Buarque, Caetano Veloso, Gilberto Gil
- Marisa Monte, Gal Costa

**Pop/Eletrônica:**
- Daft Punk, The Weeknd
- Coldplay, Imagine Dragons

### Como executar:

```bash
cd backend
source venv/bin/activate
python scripts/seed_real_data.py
```

### O que ele faz:

1. 📡 Busca cada artista na API do MusicBrainz
2. 💿 Obtém até 5 álbuns por artista
3. 🎵 Adiciona até 15 músicas por álbum
4. 📊 Popula com dados reais:
   - Títulos de músicas e álbuns
   - Anos de lançamento
   - Duração das músicas
   - Gêneros musicais
   - Biografias dos artistas

### Tempo estimado:
- ~5-10 minutos para ~26 artistas
- Rate limit: 1 request/segundo (conforme política da MusicBrainz)

### Resultado esperado:
- ~26 artistas
- ~100-130 álbuns
- ~1000-1500 músicas

## 🎸 seed_spotify_data.py

Alternativa usando Spotify API (requer credenciais).

Para usar:
1. Registre um app em https://developer.spotify.com/dashboard
2. Obtenha `client_id` e `client_secret`
3. Configure no script
4. Execute

**Vantagem:** Acesso a capas de álbuns em alta qualidade e previews de 30s.

## 📝 Notas

- O script é idempotente: pode ser executado múltiplas vezes sem duplicar dados
- Pula artistas/álbuns que já existem no banco
- Usa dados reais da maior base de dados aberta de música do mundo
- Totalmente gratuito e sem limites
