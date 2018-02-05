import datetime

from telegram import Chat, ChatMember
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler, CommandHandler, RegexHandler

from bot import db, config, schedulers
import sys

from bot.util import logger

ADDFAQ,REMINDER_TEXT,REMINDER_TARGET,REMINDER_TIME=range(4)

UNAUTHORIZED="Unauthorized! Please check with your admin. I replied you in private chat @thedalinbot"

updater=None

def faqcmd(bot, update, user_data=None):
    text=db.faq(update.message.chat_id)
    if text:
        reply(text,bot=bot,update=update)
    else:
        update.message.reply_text("FAQ not added")
    return ConversationHandler.END



def remindcmd(bot, update, user_data=None):
    if isadmin(bot, update.message.chat_id, user_id=update.effective_message.from_user.id):
        update.message.reply_text("What do you like to remind about?\n(e.g. Thedal Release)")
    else:
        update.message.reply_text(UNAUTHORIZED)
        return ConversationHandler.END
    return REMINDER_TEXT

def delremindcmd(bot, update, user_data=None):
    if isadmin(bot,update.message.chat_id,user_id=update.effective_message.from_user.id):
        deleted=db.delreminder(update.message.chat_id)
        if deleted:
            update.message.reply_text("Reminders deleted")
            deletejobs()
        else:
            update.message.reply_text('None to delete')
    else:
        update.message.reply_text(UNAUTHORIZED)

    return ConversationHandler.END


def addfaqcmd(bot, update, user_data=None):
    if isadmin(bot, update.message.chat_id, user_id=update.effective_message.from_user.id):
        update.message.reply_text('Please Add your FAQ for this group')
    else:
        update.message.reply_text(UNAUTHORIZED)
    return ADDFAQ

def addfaq(bot, update, user_data=None):
    text=update.message.text
    db.addfaq(text,update.message.chat_id)
    update.message.reply_text('FAQ Added')
    return ConversationHandler.END

def remindertxt(bot, update, user_data=None):
    text=update.message.text
    user_data['text']=text
    update.message.reply_text('How many days to go for your event?')
    return REMINDER_TARGET


def remindertgt(bot, update, user_data=None):
    text = update.message.text
    try:
        targettime=int(text)
        user_data['targettime']=targettime
        update.message.reply_text('At what time you like to nofity the group? (e.g. 04:30 or 20:30)')
        return REMINDER_TIME
    except ValueError as ve:
        update.message.reply_text('Invalid syntax. How many days to go for your event?')
        return REMINDER_TARGET

def remindertime(bot, update, user_data=None):
    text = update.message.text
    try:
        notifytime = datetime.datetime.strptime(text, '%H:%M')
        user_data['notifytime'] = text
        update.message.reply_text('Event will be reminded daily at '+text+' for next '+str(user_data['targettime'])+' days')
        db.addreminder(user_data['text'],update.message.chat_id,
                       targettime=datetime.datetime.now()+datetime.timedelta(days=user_data['targettime']),
                       notifytime=user_data['notifytime'])
        reschedulejobs()
        return ConversationHandler.END
    except :
        update.message.reply_text('Invalid syntax. At what time you like to nofity the group? (e.g. 04:30 or 20:30)')
        return REMINDER_TIME

def showremindercmd(bot,update):
    reminders=db.reminders(update.message.chat_id)
    text=''
    for reminder in reminders:
        text+=reminder.text+' on '+reminder.targettime.strftime('%d/%m/%Y')
        text+='\n'
    if text:
        update.message.reply_text(text)
    else:
        update.message.reply_text('No reminders')
    return ConversationHandler.END

def setuphandler():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('addfaq', addfaqcmd),
                      CommandHandler('faq', faqcmd),
                      CommandHandler('remind', remindcmd),
                      CommandHandler('showreminder', showremindercmd),
                      CommandHandler('delreminder', delremindcmd)
                      ],

        states={
            ADDFAQ: [MessageHandler(Filters.text,
                                    addfaq,
                                    pass_user_data=True),
                     ],
            REMINDER_TEXT: [MessageHandler(Filters.text,
                                      remindertxt,
                                      pass_user_data=True),
                       ],
            REMINDER_TARGET: [MessageHandler(Filters.text,
                                      remindertgt,
                                      pass_user_data=True),
                       ],
            REMINDER_TIME: [MessageHandler(Filters.text,
                                      remindertime,
                                      pass_user_data=True),
                       ]
        },

        fallbacks=[RegexHandler('^Done$', done, pass_user_data=True)]

    )
    return conv_handler

def done(bot, update, user_data=None):
    update.message.reply_text("Happy Day")
    return ConversationHandler.END

def newmember(bot, update):
    # here you receive a list of new members (User Objects) in a single service message
    new_members = update.message.new_chat_members
    # do your stuff here:
    for member in new_members:
        faq=db.faq(update.message.chat_id)
        if faq:
            bot.send_message(chat_id=member.id, text="Hi "+member.name+",\nWelcome to our group\n\n"+faq)

def deletejobs():
    for job in updater.job_queue.jobs():
        job.schedule_removal()

def reschedulejobs():
    deletejobs()
    schedulers.schedulejobs(updater.job_queue)

def main():

    db.initdb()

    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    # global updater
    # 535372141:AAEgx8VtahWGWWUYhFcYR0zonqIHycRMXi0   - dev token
    # 534849104:AAHGnCHl4Q3u-PauqDZ1tspUdoWzH702QQc   - live token

    token_key='LIVE_TOKEN'



    global updater

    # updater = Updater("535372141:AAEgx8VtahWGWWUYhFcYR0zonqIHycRMXi0")  #Dev

    updater = Updater(config.config['telegram'][token_key])  # Live

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(setuphandler())
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, newmember))
    dp.add_error_handler(error)

    logger.info("Starting the bot in " + ("DEV" if token_key == "DEV_TOKEN" else "LIVE"))

    # Start the Bot
    updater.start_polling()
    schedulers.schedulejobs(updater.job_queue)
    updater.idle()




def reply(text,bot=None,update=None,parsemode=None,chatid=None,reply_markup=None,disable_web_page_preview=None):
    isgroupadmin=isgroup(update) and isadmin(bot,chat_id=update.effective_message.chat_id,user_id=update.effective_message.from_user.id)
    if bot and isgroup(update) and not isgroupadmin:
        if not chatid:
            chatid=update.effective_message.from_user.id
        update.effective_message.reply_text(UNAUTHORIZED)
        bot.send_message(chat_id=chatid,text=text,
                         parse_mode=parsemode,
                         reply_markup=reply_markup,
                         disable_web_page_preview=disable_web_page_preview)

    elif update:
        update.effective_message.reply_text(text,
                                  parse_mode=parsemode,
                                  reply_markup=reply_markup,
                                  disable_web_page_preview=disable_web_page_preview)
    return isgroupadmin


def isgroup(update):
    type = update.effective_chat.type
    return (type == Chat.GROUP or type == Chat.SUPERGROUP)


def isadmin(bot,chat_id,user_id):
    status=bot.get_chat_member(chat_id, user_id).status
    return status ==ChatMember.CREATOR or status == ChatMember.ADMINISTRATOR

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

if __name__ == '__main__':
    main()