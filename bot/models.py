from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import datetime


db = SqliteExtDatabase('thedal.db')

class BaseModel(Model):
    class Meta:
        database = db

#(type text, symbol text, callrange text, misc text,
 #                user text,chatid text,userid text,time timestamp

class GroupMessage(BaseModel):

    type=IntegerField()
    text=CharField()
    chatid=CharField()
    time=DateTimeField(default=datetime.datetime.now)

    # def updateorreplace(self):
    #     self.insert(self).upsert().execute()

    class Meta:
        indexes = ((('chatid', 'type'), True),)


#(symbol text,operation text, price text, chatid text,time timestamp,
#                 PRIMARY KEY (symbol,operation,chatid))''')

class Reminder(BaseModel):
    text=CharField()
    chatid=CharField()
    targettime=DateTimeField()
    notifytime=CharField()
    misc=CharField(null=True)

    class Meta:
        indexes=((('targettime','chatid'), True), )









if __name__ == '__main__':
    # test()
    # print(getcalls('12345'))
    pass

