import datetime

from peewee import DoesNotExist

from bot.models import GroupMessage,Reminder,db
from bot.util import logger

FAQ,RULES=range(2)

def initdb():
    db.connect()
    db.create_tables([GroupMessage,Reminder],safe=True)
    db.close()


def addfaq(text,chatid):
    GroupMessage.insert(text=text,chatid=str(chatid),type=FAQ).upsert().execute()


def addreminder(text,chatid,targettime=None,notifytime=None):
    Reminder.insert(text=text,chatid=chatid,targettime=targettime,notifytime=notifytime).upsert().execute()

def delreminder(chatid):
    return Reminder.delete().where((Reminder.chatid==chatid)).execute()

def faq(chatid):
   try:
        faq= GroupMessage.select().where((GroupMessage.chatid==str(chatid)) & (GroupMessage.type==FAQ)).get()
        return faq.text
   except DoesNotExist as de:
        pass


def reminders(chatid):
    return list(Reminder.select().where((Reminder.chatid==str(chatid))))

def allreminders():
    return list(Reminder.select())