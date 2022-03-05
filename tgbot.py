import telebot
import time
import datetime
from multiprocessing import *
import schedule

bot = telebot.TeleBot('')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Привет, я бот, который вовремя напомнит о таблетках. Напиши /help, чтобы увидеть список комманд")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "/start -- запустить бота,/schedule -- вывод календаря на текущий месяц,/starttimer -- включает напоминающие о приеме таблеток уведомления. Запустить необходимо в день приема таблеток согласно расписанию (/schedule)")
    elif message.text == "/schedule":
        bot.send_message(message.from_user.id, "Прием бики на март: 3, 6, 9, 12, 15, 18, 21, 24, 27, 30")
    elif message.text == "/starttimer":
        bot.send_message1(message.from_user.id,'Пора выпить таблетку! <<переодичность отправки уведомлений 3 дня>>')
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

def start_process():
    p1 = Process(target=P_schedule.start_schedule, args=())
    p1.start()


class P_schedule():
    def start_schedule():

        schedule.every(3).days.at("00:00").do(P_schedule.send_message1)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def send_message1():
        bot.send_message(USER_ID, 'Отправка сообщения по времени')

if __name__ == '__main__':
    start_process()
    try:
        bot.polling(none_stop=True)
    except:
        pass
