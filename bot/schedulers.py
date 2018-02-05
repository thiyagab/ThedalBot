import datetime

from bot import db
from bot.util import logger


def notify(bot,job):
    text=job.context['text']
    delta = job.context['time'].replace(hour=0,minute=0,second=0,microsecond=0)-datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)

    if delta.days>0:
        text=text+' in '+str(delta.days)+' day(s)'
        bot.send_message(chat_id=job.context['chatid'],text=text)
    else:
        db.delreminder(job.context['chatid'])
        job.schedule_removal()



def schedulejobs(job_queue):
    logger.info("Scheduling jobs..")
    reminders=db.allreminders()
    for reminder in reminders:
        context={}
        context['text']=reminder.text
        context['time']=reminder.targettime
        context['chatid']=reminder.chatid
        time=reminder.notifytime.split(":")
        now=datetime.datetime.now()
        hour= int(time[0])
        minute = int(time[1])
        if now.hour >= hour and now.minute > minute:
            now+=datetime.timedelta(days=1)
        now=now.replace(hour=hour,minute=minute,second=0)
        job_queue.run_repeating(callback=notify, interval=24 * 60 * 60, first=now,context=context)
        # job_queue.bot.send_message(chat_id=context['chatid'],text='Test')


    return None

def main():
    db.initdb()
    #
    db.deleteevents()
    # print(db.getevents())
    text=''
    # print(len(names))
    # print(names)



if __name__ == '__main__':
    main()
