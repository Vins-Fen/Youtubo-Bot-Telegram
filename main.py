import googleapiclient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application,  CallbackQueryHandler, ContextTypes
from googleapiclient.discovery import build
import logging
from dotenv import load_dotenv
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent / "api.env"
load_dotenv(dotenv_path=ENV_PATH,
    override=True,)
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.helpers import escape_markdown
from Video import extract_video_id, prendi_tag_da_youtube,get_category
from Youtuber import  salva_su_file, newYoutuber, get_channel_id_from_handle
from User import  initUser, saveuser
import json
import os

API_TOKEN =os.getenv("TELEGRAM_TOKEN_API")
API_YOUTUBE_TOKEN =os.getenv("YOUTUBE_TOKEN_API")
GRUPPI_AUTORIZZATI=[os.getenv("GRUPPI_AUTORIZZATI")]
CANALI_AUTORIZZATI=[os.getenv("CANALI_AUTORIZZATI")]
googleapiclient.discovery.cache = None


if not API_TOKEN:
    raise RuntimeError(
        f"TELEGRAM_TOKEN_API non trovato nel file {ENV_PATH}"
    )


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

    chat_type = update.message.chat.type
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



PRIMO_VIDEO = 0
SECONDO_VIDEO = 1
async def avvia_video(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            "📹 Invia il primo video"
        )
    else:
        await update.message.reply_text(
            "📹 Invia il primo video"
        )

    return PRIMO_VIDEO
async def ricevi_primo_video(update, context):
    context.user_data["video1"] = update.message.text.strip()
    await update.message.reply_text("📹 Ora invia il secondo video")
    return SECONDO_VIDEO

async def ricevi_secondo_video(update, context):
    context.user_data["video2"] = update.message.text.strip()

    v1 = context.user_data["video1"]
    v2 = context.user_data["video2"]

    commonTags : list[str]= confronta_tag(v1,v2)
    context.user_data["commonTags"] = commonTags
    await update.message.reply_text(f"✅ Tag in comune: \n {context.user_data["commonTags"]} \n")

    return ConversationHandler.END

async def annulla(update, context):
    await update.message.reply_text("❌ Conversazione annullata.")
    return ConversationHandler.END

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id= query.from_user.id
    if query.data == "inserisci_video":
        await query.message.reply_text("🔹 Condividi un video sul gruppo")
        pending_users[user_id] = "inserisci_video"
        await query.message.reply_text(
            "Inserisci il link del video che vuoi condividere ❤️‍🔥"
        )

    elif query.data == "counter_iscritti":
        await query.message.reply_text("📊Mandami il tuo chanel Id ")
        pending_users[user_id] = "counter_iscritti"
    elif query.data == "faq":
        await query.message.reply_text("❓ Stai per creare una FAQ per il gruppo.")
        pending_users[user_id] = "faq"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id


    if user_id in pending_users and pending_users[user_id] == "counter_iscritti":
        channel_id = None
        input_text = update.message.text.strip()
        if input_text.startswith("UC"):
            channel_id = input_text

        elif input_text.startswith("@"):
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

                salva_su_file(youtuber, filename="youtubers.json")
                await invia_classifica_canale(context)


            else:
                await update.message.reply_text("❌ Errore: Channel ID non valido. Riprova.")
        else:
            await update.message.reply_text(
                "❌ Non ho trovato nessun canale con questo handle. Prova con il Channel ID!")

        del pending_users[user_id]
    if user_id in pending_users and pending_users[user_id] == "inserisci_video":
       await  video_handler(update, context)
    if user_id in pending_users and pending_users[user_id] == "faq":
        await faq_reciever(update, context)



async def video_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id
    input_text = update.message.text.strip()

    if pending_users.get(user_id) != "inserisci_video":
        return

    await context.bot.send_message(
        chat_id=GRUPPI_AUTORIZZATI[0],
        text=input_text,
    )

    await update.message.reply_text(
        "✅ Video condiviso correttamente."
    )

    pending_users.pop(user_id, None)


def confronta_tag(v1,v2) ->list[str]:
    commonTags: list[str] = []
    id = extract_video_id(v1)
    id2 = extract_video_id(v2)

    tags1 = prendi_tag_da_youtube(id)
    tags2 = prendi_tag_da_youtube(id2)
    for tag in tags1:
        if tag in tags2 and tag not in commonTags:
            commonTags.append(tag)

    return commonTags


def genera_messaggio_counter(filename: str = "youtubers.json") -> str:
    try:
        with open(filename, "r") as file:
                data = json.load(file)

        if not data:
            return "⚠️ Nessun dato disponibile sui canali YouTube."

        data.sort(key=lambda x: int(x["counter_followers"]), reverse=True)
        message = "📊 *Classifica Canali YouTube* 📊\n\n"
        for i, youtuber in enumerate(data, start=1):
            message += f"\n 🏆 {i}. {youtuber['yid']}  {youtuber['counter_followers']} iscritti\n"

        return message
    except FileNotFoundError:
        return "❌ Errore: Il file json non esiste!"
    except Exception as e:
        return f"⚠️ Errore durante la lettura del file: {str(e), str(e.args)}"

async def invia_classifica_canale(context: ContextTypes.DEFAULT_TYPE):
    chat_id = CANALI_AUTORIZZATI[0]
    message = genera_messaggio_counter("youtubers.json")
    safe_message = escape_markdown(message, version=2)

    try:
        await context.bot.send_message(chat_id=chat_id, text=safe_message, parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Errore nell'invio del messaggio: {e}")


async def messaggio_gruppo(update: Update, context):
    chat_id = update.message.chat_id
    if chat_id in GRUPPI_AUTORIZZATI:
        await context.bot.send_message(chat_id=chat_id, text="✅ Messaggio inviato solo ai gruppi autorizzati!")
    else:
        await update.message.reply_text("❌ Questo gruppo non è autorizzato a ricevere messaggi.")

async def faq_reciever(update: Update, context):
    input_text = update.message.text.strip()
    user_username= update.message.from_user.username or "utente senza username"
    user_id = update.message.from_user.id

    await context.bot.send_message(
        chat_id="@youtubersIt",
        text=f"Domanda da {user_username}:\n{input_text}",
    )

    pending_users.pop(user_id, None)

    await update.message.reply_text(
        "✅ Domanda inviata correttamente."
    )




def main():
    app = Application.builder().token(API_TOKEN).build()


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("video", avvia_video),
                      CallbackQueryHandler(avvia_video, pattern="^tags$")],
        states={
            PRIMO_VIDEO: [MessageHandler(filters.TEXT & ~filters.COMMAND , ricevi_primo_video)],
            SECONDO_VIDEO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_secondo_video)],
        },
        fallbacks=[CommandHandler("cancel", annulla)],
    )


    app.add_handler(conv_handler)

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("mex_bot", messaggio_gruppo))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("tipo", get_category))


    logger.info("Bot in esecuzione...")
    app.run_polling()


if __name__ == "__main__":
    main()


