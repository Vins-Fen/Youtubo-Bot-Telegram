from openpyxl.styles.builtins import title
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, ContextTypes, MessageHandler, filters
from googleapiclient.discovery import build

from Video import Video,get_video_info
from Youtuber import Youtuber, salva_su_file, newYoutuber, to_dict, add_video
from User import User, initUser, to_dict, saveuser
import json

API_TOKEN = "8136102745:AAHpfXtCRku9aI5E9TrBFckz1KgsbJg0ljA"
API_YOUTUBE_TOKEN="AIzaSyDnXyjJ7CltocH4RjDFf7D3S5lKfXHMssM"

pending_users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id= update.effective_user.id
    username= update.effective_user.username
    user= initUser(user_id, username)
    saveuser(user, "user.json")
    keyboard = [
        [InlineKeyboardButton(" Condividi un video 🎥", callback_data="inserisci_video")],
        [InlineKeyboardButton("Counter Iscritti 📊", callback_data="counter_iscritti")],
        [InlineKeyboardButton("FAQ ❓", callback_data="faq")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Benvenuto in CDY!\n Sono un alfa, il mio scopo è quello di semplificarti la vita\n score:"+ str(user.score) + ""+"\nScegli un'opzione:", reply_markup=reply_markup)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sto chiudendo il bot... 🚫")
    await context.application.stop()

async def is_admin(update: Update, context: CallbackContext) -> bool:
    """Controlla se l'utente è un admin nel gruppo."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    chat_admins = await context.bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in chat_admins]

    return user_id in admin_ids


# ✅ Funzione per ottenere il numero di iscritti da YouTube
def youtube_sub(chanel_Id):
    youtube = build('youtube', 'v3', developerKey= API_YOUTUBE_TOKEN)

    request= youtube.channels.list(
        part='statistics',
        id=chanel_Id
    )
    response=request.execute()

    if "items" in response and len(response["items"]) > 0:
        subscribers= response["items"][0]["subscribers"]
        return int(subscribers)
    else:
        return None


def get_channel_id_from_handle(youtube_handle):
    if youtube_handle.startswith("@"):  # Rimuove il simbolo '@' se presente
        youtube_handle = youtube_handle[1:]

    youtube = build("youtube", "v3", developerKey=API_YOUTUBE_TOKEN)

    try:
        request = youtube.search().list(
            part="snippet",
            q=youtube_handle,
            type="channel",
            maxResults=1
        )
        response = request.execute()

        if "items" in response and len(response["items"]) > 0:
            channel_id = response["items"][0]["id"]["channelId"]
            return channel_id
        else:
            return None
    except Exception as e:
        print("Errore API YouTube:", e)
        return None


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query  # Otteniamo l'oggetto della query
    await query.answer()  # Conferma che abbiamo ricevuto il click

    # Controlliamo quale pulsante è stato premuto
    if query.data == "inserisci_video":
        await query.message.reply_text("🔹 Condividi un video sul gruppo")
        pending_users[query.data] =  "inserisci_video"
    elif query.data == "counter_iscritti":
        await query.message.reply_text("📊Mandami il tuo chanel Id ")
        pending_users[query.from_user.id] = "counter_iscritti"
    elif query.data == "faq":
        await query.message.reply_text("❓ Stai per creare una FAQ per il gruppo.")

# ✅ Funzione per ricevere il Channel ID e mostrare gli iscritti
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        input_text = update.message.text.strip()  # Rimuove eventuali spazi

        if user_id in pending_users and pending_users[user_id] == "counter_iscritti":
            channel_id = None

            if input_text.startswith("UC"):
                # Se l'input è già un Channel ID
                channel_id = input_text
            elif input_text.startswith("@"):
                # Se l'input è un YouTube Handle, convertiamolo in Channel ID
                channel_id = get_channel_id_from_handle(input_text)

            if channel_id:
                youtube = build("youtube", "v3", developerKey=API_YOUTUBE_TOKEN)
                request = youtube.channels().list(part="snippet,statistics", id=channel_id)
                response = request.execute()

                if "items" in response and len(response["items"]) > 0:
                    channel_info = response["items"][0]
                    nome_canale = channel_info["snippet"]["title"]
                    subscribers = int(channel_info["statistics"]["subscriberCount"])
                    tot_view=int(channel_info["statistics"]["viewCount"])
                    youtuber= newYoutuber(nome_canale, user_id, input_text, subscribers, tot_view)

                    await update.message.reply_text(f"✅ Il tuo canale *{nome_canale}* ha **{subscribers} iscritti**! 🎉",
                                                    parse_mode="Markdown")

                    # Salviamo il canale e aggiorniamo la lista
                    salva_su_file(youtuber, filename= "youtubers.json")
                else:
                    await update.message.reply_text("❌ Errore: Channel ID non valido. Riprova.")
            else:
                await update.message.reply_text(
                    "❌ Non ho trovato nessun canale con questo handle. Prova con il Channel ID!")

            del pending_users[user_id]  # Rimuoviamo l'utente dalla lista di attes

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    input_text = update.message.text.strip()


    if user_id in pending_users and pending_users[user_id] == "inserisci_video":
        # qua raggruppo tutto in una funzione
        query = update.callback_query
        query.message.reply_text("Inserisci il link del video che vuoi condividere❤️‍🔥")
        link = update.message.text
        video_info = get_video_info(link)

        if video_info:
            video = Video(video_info["title"], link, video_info["views"], video_info["likes"],
                          video_info["comment_count"])
            print(type(video))
            # qui devo fare un controllo per vedere se l'user id è associato ad uno youtuber
            # add_video(user_id,video)


def main():
    app = Application.builder().token(API_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot in esecuzione...")
    app.run_polling()

if __name__ == "__main__":
    main()