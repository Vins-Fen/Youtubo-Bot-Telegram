# Youtubo-Bot-Telegram

Bot Telegram per la community **CDY**, pensato per aiutare creator YouTube a condividere video, confrontare tag, monitorare gli iscritti dei propri canali e interagire con la community tramite FAQ.

## ✨ Funzionalità

- **Condivisione video** — gli utenti possono condividere link di video YouTube direttamente nel gruppo autorizzato.
- **Confronto tag** (`/video`) — confronta i tag di due video YouTube e restituisce quelli in comune, utile per ottimizzare la SEO dei propri contenuti.
- **Counter iscritti** — inviando il Channel ID (o l'handle `@canale`) di un canale YouTube, il bot recupera nome canale, numero di iscritti e visualizzazioni totali, salvando i dati e aggiornando una classifica dei canali registrati.
- **Classifica canali** — genera e invia automaticamente una classifica dei canali YouTube registrati, ordinata per numero di iscritti.
- **FAQ** — gli utenti possono inviare domande che vengono reindirizzate a un canale Telegram dedicato.
- **Gestione utenti** — ogni utente Telegram viene salvato/aggiornato con un punteggio (`score`) tramite `User.py`.
- **Menu interattivo** — tastiera inline su chat privata con accesso rapido a tutte le funzioni.

## 🛠️ Stack tecnico

- **Python 3**
- [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot) — gestione bot e handler Telegram
- [`google-api-python-client`](https://github.com/googleapis/google-api-python-client) — accesso alla YouTube Data API v3
- `python-dotenv` — gestione delle variabili d'ambiente
- `pymongo` — (predisposto per integrazione database MongoDB)
- File JSON (`user.json`, `youtubers.json`) per la persistenza dati

## 📂 Struttura del progetto

```
.
├── main.py          # entry point, handler dei comandi e dei messaggi Telegram
├── Video.py         # logica relativa ai video (estrazione info, tag YouTube)
├── Youtuber.py      # gestione canali YouTube registrati e classifica
├── User.py          # gestione utenti Telegram e relativo punteggio
├── Admin            # funzionalità/script amministrativi
├── user.json        # storage utenti registrati
├── youtubers.json   # storage canali YouTube registrati
└── .gitignore
```

## ⚙️ Configurazione

Il bot richiede un file `.env` nella root del progetto (**non incluso nel repository** per motivi di sicurezza) con le seguenti variabili:

```env
TELEGRAM_TOKEN_API=il_tuo_token_telegram
YOUTUBE_TOKEN_API=la_tua_api_key_youtube
GRUPPI_AUTORIZZATI=id_gruppo_telegram_autorizzato
CANALI_AUTORIZZATI=id_canale_telegram_autorizzato
```

- `TELEGRAM_TOKEN_API`: token del bot ottenuto da [@BotFather](https://t.me/BotFather)
- `YOUTUBE_TOKEN_API`: API key della [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com), generata da Google Cloud Console
- `GRUPPI_AUTORIZZATI`: ID del gruppo/i Telegram autorizzato a ricevere i video condivisi
- `CANALI_AUTORIZZATI`: ID del canale Telegram autorizzato a ricevere la classifica canali

> ⚠️ **Non committare mai il file `.env`** — assicurati che sia presente nel `.gitignore`.

## ▶️ Avvio del bot

1. Clona il repository:
   ```bash
   git clone https://github.com/Vins-Fen/Youtubo-Bot-Telegram.git
   cd Youtubo-Bot-Telegram
   ```

2. Installa le dipendenze:
   ```bash
   pip install python-telegram-bot google-api-python-client python-dotenv pymongo
   ```

3. Crea il file `.env` come descritto sopra.

4. Avvia il bot:
   ```bash
   python main.py
   ```

## 🤖 Comandi disponibili

| Comando | Descrizione |
|---|---|
| `/start` | Avvia il bot e mostra il menu principale |
| `/stop` | Arresta il bot |
| `/video` | Avvia il confronto tag tra due video YouTube |
| `/cancel` | Annulla la conversazione in corso |
| `/getchatId` | Restituisce l'ID della chat corrente |

## 🔐 Sicurezza

Le credenziali (token Telegram, API key YouTube) sono gestite esclusivamente tramite variabili d'ambiente caricate da `.env` con `python-dotenv`, e non devono mai essere inserite direttamente nel codice o committate su Git.

## 📄 Licenza

Progetto sviluppato a scopo personale/didattico per la community CDY.
