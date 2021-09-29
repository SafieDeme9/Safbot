import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler,ConversationHandler, MessageHandler, Filters, CallbackContext
import random
from telegram.ext import dispatcher

from telegram.ext.dispatcher import Dispatcher 

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text("""
    Bienvenue sur le bot Saf bot un bot en plein depart.

    Les commandes disponibles sont :
    - /start pour commencer
    - /help si vous avez besoin d'aide
    - /discuter pour discuter avec moi
        """)

def help(update: Update, context : CallbackContext) -> None:
    """Send a help message"""
    update.message.reply_text("""
    Saf s'ennuie et a besoin de compagnie. Discuter avec elle (/discuter) elle est très intéressante et surtout célibataire.
        """)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Desolée, j'ai pas compris ce que vous vouliez faire.")


GENDER, PHOTO, LOCATION, BIO = range(4)
def discuter(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [['Garcon', 'Fille', 'Chepa']]

    update.message.reply_text(
        'Ah! Merci de me tenir compagnie je m\'ennuyais lol !\n'
        'Si vous voulez plus me parler appuyez sur /cancel.\n\n'
        'Alors dites moi vous êtes un garçon ou une fille? (J\'essaie pas de vous pecho. Promis!)',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Garcon ou fille?'
        ),
    )

    return GENDER


def gender(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Alors %s tu es %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Envoyez une photo de vous svp, '
        'histoire de mettre un visage sur votre nom, ou /skip si vous voulez pas. Vous n\'êtes pas obligé(e)'
        '\n\nSi vous voulez mettre fin à la discussion vous pouvez /cancel',
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO

def photo(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'On s\'est déjà vu quelque part, non? Vous ressemblez énormément à mon prochain rencard.'
        '\nDites moi vous habitez où ?\n /skip si vous voulez pas dire. (Action qui va probablement beaucoup m\'attrister.) '
        '\n\nSi vous voulez mettre fin à la discussion vous pouvez /cancel'
    )
    return LOCATION
 
def skip_photo(update: Update, context: CallbackContext) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'Dommage ! Je ne saurais pas à quoi vous ressembler. Ca m\'attriste énormément. \nAu moins dites moi où habitez vous. Vous pouvez /skip si vous voulez pas.'
        '\n\nSi vous voulez mettre fin à la discussion vous pouvez /cancel'
    )

    return LOCATION


def location(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    logger.info(
        "Location of %s: ", user.first_name
    )
    update.message.reply_text(
        'Aight ! Je vais passer demain dire bonjour à mes futurs beaux parents.\nParlez moi un peu de vous.'
        '\n\nSi vous voulez mettre fin à la discussion vous pouvez /cancel'
    )

    return BIO


def skip_location(update: Update, context: CallbackContext) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text(
        'Je suis triste :/. J\'aurais bien aimé vous rendre visite un de ces 4. Mais bon! Parlez moi de vous au moins'
        '\n\nSi vous voulez mettre fin à la discussion vous pouvez /cancel'
    )

    return BIO

def bio(update: Update, context: CallbackContext) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Wow ! Impressionnant. \n\nMerci beaucoup pour la discussion. Ce fut un plaisir.\nRendez-vous à nos fiançailles haha!')

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Merci beaucoup pour la discussion j\'espere qu\'on se reparlera bientot.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater('TOKEN')

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('discuter', discuter)],
        states={
            GENDER: [MessageHandler(Filters.regex('^(Garcon|Fille|Chepa)$'), gender)],
            PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
            LOCATION: [
                MessageHandler(Filters.text & ~Filters.command, location),
                CommandHandler('skip', skip_location),
            ],
            BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()