from contextlib import nullcontext

import googleapiclient
from googleapiclient.errors import HttpError
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, ContextTypes, \
    MessageHandler, filters, ApplicationBuilder
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import pymongo as mongo
import logging
from dotenv import load_dotenv
import os
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler

from telegram.helpers import escape_markdown

from Video import Video, get_video_info, extract_video_id, prendi_tag_da_youtube,get_category,get_category_name
from Youtuber import Youtuber, salva_su_file, newYoutuber, add_video, get_channel_id_from_handle
from User import User, initUser, to_dict, saveuser, user_exists
import json
load_dotenv()

API_TOKEN =os.getenv("TELEGRAM_TOKEN_API")
API_YOUTUBE_TOKEN =os.getenv("YOUTUBE_TOKEN_API")
GRUPPI_AUTORIZZATI=[os.getenv("GRUPPI_AUTORIZZATI")]
CANALI_AUTORIZZATI=[os.getenv("CANALI_AUTORIZZATI")]
googleapiclient.discovery.cache = None  # Disattiva la cache per evitare warning


pending_users = {}
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    user = initUser(user_id, username)
    saveuser(user, "user.json")

    #mettere gli user in un database
    #chat_id = update.message.chat_id
    chat_type = update.message.chat.type  # Ottieni il tipo di chat
    if chat_type== 'private':
        keyboard = [
            [InlineKeyboardButton(" Condividi un video 🎥", callback_data="inserisci_video")],
            [InlineKeyboardButton("Counter Iscritti 📊", callback_data="counter_iscritti")],
            [InlineKeyboardButton("FAQ ❓", callback_data="faq")],
            [InlineKeyboardButton("Confronta Tags ⚖️", callback_data="tags")],

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Benvenuto in CDY!\n Sono un alfa, il mio scopo è quello di semplificarti la vita\n score:" + str(
                user.score) + "" + "\nScegli un'opzione:", reply_markup=reply_markup)
    elif chat_type in ["group", "supergroup"]:
        await update.message.reply_text(
            "👋 Benvenuti nella community che vi permette di riscoprire i vostri video e la bellezza di crearli sotto una luce diversa: quella della condivisione!"
        )


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


PRIMO_VIDEO = 0
SECONDO_VIDEO = 1

async def avvia_video(update, context):
    query = update.callback_query
    if query.message:
        await query.message.reply_text('📹 Invia il primo video')
        return PRIMO_VIDEO
    else:
        await update.message.reply_text("📹 Invia il primo video")
        return PRIMO_VIDEO   # si passa allo stato PRIMO_VIDEO

async def ricevi_primo_video(update, context):
    context.user_data["video1"] = update.message.text.strip()
    await update.message.reply_text("📹 Ora invia il secondo video")
    return SECONDO_VIDEO   # si passa allo stato SECONDO_VIDEO

async def ricevi_secondo_video(update, context):
    context.user_data["video2"] = update.message.text.strip()

    v1 = context.user_data["video1"]
    v2 = context.user_data["video2"]

    commonTags : list[str]= confronta_tag(v1,v2)
    context.user_data["commonTags"] = commonTags
    await update.message.reply_text(f"✅ Tag in comune: \n {context.user_data["commonTags"]} \n")

    return ConversationHandler.END   # fine conversazione

async def annulla(update, context):
    await update.message.reply_text("❌ Conversazione annullata.")
    return ConversationHandler.END



# ✅ Funzione per ottenere il numero di iscritti da YouTube
def youtube_sub(chanel_Id):
    youtube = build('youtube', 'v3', developerKey=API_YOUTUBE_TOKEN)

    request = youtube.channels.list(
        part='statistics',
        id=chanel_Id
    )
    response = request.execute()

    if "items" in response and len(response["items"]) > 0:
        subscribers = response["items"][0]["subscribers"]
        return int(subscribers)
    else:
        return None


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query  # Otteniamo l'oggetto della query
    await query.answer()  # Conferma che abbiamo ricevuto il click
    user_id= query.from_user.id
    # Controlliamo quale pulsante è stato premuto
    if query.data == "inserisci_video":
        print(f"🔘 Button click: {query.data} da {user_id}")
        await query.message.reply_text("🔹 Condividi un video sul gruppo")
        pending_users[user_id] = "inserisci_video"

    elif query.data == "counter_iscritti":
        await query.message.reply_text("📊Mandami il tuo chanel Id ")
        pending_users[user_id] = "counter_iscritti"
    elif query.data == "faq":
        await query.message.reply_text("❓ Stai per creare una FAQ per il gruppo.")
        pending_users[user_id] = "faq"
    elif query.data == "tags":
        await query.message.reply_text("Confrontiamo i tag")
        pending_users[user_id] = "tags"
        await video_handler(update, context)


# ✅ Funzione per gestire i messaggi di testo e i bottoni premuti
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("handlemessage")
    user_id = update.message.from_user.id


    if user_id in pending_users and pending_users[user_id] == "counter_iscritti":
        channel_id = None
        #getchannelId
        input_text = update.message.text.strip()  # Rimuove eventuali spazi
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
                tot_view = int(channel_info["statistics"]["viewCount"])
                youtuber = newYoutuber( nome_canale, user_id, input_text, subscribers, tot_view)


                await update.message.reply_text(f"✅ Il tuo canale *{nome_canale}* ha **{subscribers} iscritti**! 🎉",
                                                parse_mode="Markdown")

                # Salviamo il canale e aggiorniamo la lista
                salva_su_file(youtuber, filename="youtubers.json")
                await invia_classifica_canale(context)


            else:
                await update.message.reply_text("❌ Errore: Channel ID non valido. Riprova.")
        else:
            await update.message.reply_text(
                "❌ Non ho trovato nessun canale con questo handle. Prova con il Channel ID!")

        del pending_users[user_id]  # Rimuoviamo l'utente dalla lista di attes

    if user_id in pending_users and pending_users[user_id] == "inserisci_video":
       await  video_handler(update, context)
      #  await update.message.reply_text("Inserisci il link del video che vuoi condividere❤️‍🔥")
    if user_id in pending_users and pending_users[user_id] == "faq":
        print("test faq")
        await faq_reciever(update, context)
    if user_id in pending_users and pending_users[user_id] == "tags":
        print("test tags")
        await video_handler(update, context)




async def video_handler(update: Update, context, videos=None):
    await get_user_id(update, context)
    if videos is None:
        videos = []
    if update.callback_query:  # click su bottone
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()  # risponde a Telegram per rimuovere il “loading”
        if query.data== 'tags' :
            await avvia_video(update, context)


    user_id = update.message.from_user.id
    input_text = update.message.text.strip()
    if pending_users[user_id] == "inserisci_video":

        await update.message.reply_text("Inserisci il link del video che vuoi condividere❤️‍🔥")
        await context.bot.send_message(chat_id=GRUPPI_AUTORIZZATI[0], text=input_text)


    del pending_users[user_id]




def confronta_tag(v1,v2) ->list[str]:
    commonTags: list[str] = []
    id = extract_video_id(v1)
    id2 = extract_video_id(v2)

    tags1 = prendi_tag_da_youtube(id)
    tags2 = prendi_tag_da_youtube(id2)
    for tag in tags1:
        if tag in tags2 and tag not in commonTags:
            commonTags.append(tag)

            print("Tag in comune:", commonTags)
            return commonTags

import csv
async def parselink(update: Update, context: ContextTypes.DEFAULT_TYPE, input_text, option, user_id= None) -> Video :
    raw_link = input_text
    link = extract_video_id(raw_link)
    video_info = []
    video = None
    user_id= get_user_id(update, context)
    if link:
        video_info = get_video_info(link)
        # Procedi con l'elaborazione del video_info...
    else:
        await update.message.reply_text("❌ Link non valido. Assicurati di inserire un link di YouTube corretto.")
        await video_handler(update, context, user_id)

    if video_info:
        if option ==1:
            video = Video(video_info["title"], link, video_info["views"], video_info["likes"], video_info["comments"], video_info["tags"])
            print(type(video))
        else:
            await get_user_id(update, context)


        # qui devo fare un controllo per vedere se l'user id è associato ad uno youtuber
        user_id = update.effective_user.id
        if user_exists(user_id):
            add_video(user_id, video)

        await update.message.reply_text(f"✅ Video '{video_info['title']}' salvato con successo! 🎥")
        return video
    else:
        await update.message.reply_text(
            "❌ Errore: non sono riuscito a recuperare le informazioni del video. Assicurati che il link sia corretto.")



def genera_messaggio_counter(filename: str = "youtubers.json") -> str:
    try:
        with open(filename, "r") as file:
                data = json.load(file)

        if not data:
            return "⚠️ Nessun dato disponibile sui canali YouTube."

        # Ordina in base a 'counter_followers'
        data.sort(key=lambda x: int(x["counter_followers"]), reverse=True)

        # Crea il messaggio usando la sintassi MarkdownV2 corretta
        message = "📊 *Classifica Canali YouTube* 📊\n\n"
        for i, youtuber in enumerate(data, start=1):
            # Usa un singolo asterisco per il grassetto
            message += f"\n 🏆 {i}. {youtuber['yid']}  {youtuber['counter_followers']} iscritti\n"

        return message
    except FileNotFoundError:
        return "❌ Errore: Il file json non esiste!"
    except Exception as e:
        return f"⚠️ Errore durante la lettura del file: {str(e), str(e.args)}"

async def invia_classifica_canale(context: ContextTypes.DEFAULT_TYPE):
    chat_id = CANALI_AUTORIZZATI
    message = genera_messaggio_counter("youtubers.json")
    safe_message = escape_markdown(message, version=2)

    try:
        await context.bot.send_message(chat_id=chat_id, text=safe_message, parse_mode="MarkdownV2")
    except Exception as e:
        print(f"Errore nell'invio del messaggio: {e}")


async def messaggio_gruppo(update: Update, context):
    chat_id = update.message.chat_id  # Ottieni l'ID del gruppo
    print(chat_id)
    if chat_id in GRUPPI_AUTORIZZATI:
        await context.bot.send_message(chat_id=chat_id, text="✅ Messaggio inviato solo ai gruppi autorizzati!")
    else:
        await update.message.reply_text("❌ Questo gruppo non è autorizzato a ricevere messaggi.")

#invia un messaggio ad un canale
async def faq_reciever(update: Update, context):
    input_text = update.message.text.strip()
    user_username= update.message.from_user.username
    chat_id = "@youtubersIt"
    await context.bot.send_message(chat_id= chat_id, text= "Domanda da " + str(user_username) + ":\n" + input_text, parse_mode="MarkdownV2")

async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id=None):
    if update.message:
        user_id = update.message.from_user.id
        text = update.message.text
    elif update.channel_post:
        user_id = update.channel_post.chat.id
        text = update.channel_post.text

    return user_id  # Update non riconosciuto






def main():
    app = Application.builder().token(API_TOKEN).build()


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("video", avvia_video),
                      CallbackQueryHandler(avvia_video, pattern="^tags$")],  # comando per avviare la conversazione
        states={
            PRIMO_VIDEO: [MessageHandler(filters.TEXT , ricevi_primo_video)],
            SECONDO_VIDEO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_secondo_video)],
        },
        fallbacks=[CommandHandler("cancel", annulla)],  # comando per uscire
    )
    fallbacks=[CommandHandler("cancel", annulla)],


    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(video_handler,pattern="^tags$"))

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("test", messaggio_gruppo))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("tipo", get_category))
    app.add_handler(CommandHandler("getchatId", get_user_id))

    print(app.handlers)

    print("Bot in esecuzione...")
    app.run_polling()


if __name__ == "__main__":
    main()


