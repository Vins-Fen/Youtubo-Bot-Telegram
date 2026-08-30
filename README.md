[🇮🇹 Italiano](#italiano) | [🇬🇧 English](#english)


## English 

# Youtubo-Bot-Telegram

A Telegram bot built for the **CDY** community, designed to help YouTube creators share videos, compare tags, track subscriber counts of their channels, and interact with the community through FAQs.

## ✨ Features

- **Video Sharing** — Users can share YouTube video links directly in the authorized group.
- **Tag Comparison** (`/video`) — Compares the tags of two YouTube videos and returns the ones in common, useful for optimizing content SEO.
- **Subscriber Counter** — By sending the Channel ID (or the `@channel` handle) of a YouTube channel, the bot retrieves the channel name, subscriber count, and total views, saving the data and updating a leaderboard of registered channels.
- **Channel Leaderboard** — Automatically generates and sends a leaderboard of registered YouTube channels, ranked by subscriber count.
- **FAQ Handling** — Users can submit questions, which are forwarded to a dedicated Telegram channel.
- **User Management** — Each Telegram user is saved/updated with a score, managed via `User.py`.
- **Interactive Menu** — Inline keyboard in private chat for quick access to all bot features.

## 🛠️ Tech Stack

- **Python 3**
- [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot) — Telegram bot and handler management
- [`google-api-python-client`](https://github.com/googleapis/google-api-python-client) — Access to the YouTube Data API v3
- `python-dotenv` — Environment variable management
- `pymongo` — (Prepared for MongoDB database integration)
- JSON Files (`user.json`, `youtubers.json`) for data persistence

## 📂 Project Structure

```
.
├── main.py          # Entry point, command handlers, and Telegram message loops
├── Video.py         # Video logic (info extraction, YouTube tag comparison)
├── Youtuber.py      # Management of registered YouTube channels & leaderboard
├── User.py          # Telegram user management and scoring system
├── Admin            # Administrative features and scripts
├── user.json        # Storage for registered users
├── youtubers.json   # Storage for registered YouTube channels
└── .gitignore
```

## ⚙️ Setup & Configuration

The bot requires a `.env` file in the project root directory (**not included in the repository** for security reasons) with the following environment variables:

```env
TELEGRAM_TOKEN_API=your_telegram_bot_token
YOUTUBE_TOKEN_API=your_youtube_api_key
GRUPPI_AUTORIZZATI=authorized_telegram_group_id
CANALI_AUTORIZZATI=authorized_telegram_channel_id
```

- `TELEGRAM_TOKEN_API`: Bot token obtained from [@BotFather](https://t.me/BotFather)
- `YOUTUBE_TOKEN_API`: API key for the [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com), generated via Google Cloud Console
- `GRUPPI_AUTORIZZATI`: ID of the Telegram group(s) authorized to receive shared videos
- `CANALI_AUTORIZZATI`: ID of the Telegram channel authorized to receive the channel leaderboard

> ⚠️ **Never commit your `.env` file** — make sure it is listed in your `.gitignore`.

## ▶️ How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/Vins-Fen/Youtubo-Bot-Telegram.git
   cd Youtubo-Bot-Telegram
   ```

2. Install dependencies:
   ```bash
   pip install python-telegram-bot google-api-python-client python-dotenv pymongo
   ```

3. Create the `.env` file as described above.

4. Start the bot:
   ```bash
   python main.py
   ```

## 🤖 Available Commands

| Command | Description |
|---|---|
| `/start` | Launches the bot and displays the main menu |
| `/stop` | Stops the bot |
| `/video` | Starts the tag comparison between two YouTube videos |
| `/cancel` | Cancels the current conversation flow |
| `/getchatId` | Returns the current chat ID |

## 🔐 Security

Credentials (Telegram token, YouTube API key) are managed exclusively through environment variables loaded from `.env` via `python-dotenv`, and must never be hardcoded in the code or committed to Git.

## 📄 License

Project developed for personal/educational purposes for the CDY community.
## Italiano
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
