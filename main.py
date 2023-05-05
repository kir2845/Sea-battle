import telebot
from extensions import ConvertionException, CryptoConverter
from config import keys, TOKEN

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands = ['start'])
def send_welcome(message):
    bot.reply_to(message, f'Привет-привет, {message.chat.username}!\nДля получения инструкции набери команду /help\n\
или просто нажми на неё')

@bot.message_handler(commands = ['help'])
def help(message):
    text = 'Чтобы начать работу введи боту команду в следующем формате: \n\n< имя валюты, которая интересует >  \
< имя конвертируемой валюты >  < количество интересуемой валюты >\nНапример, евро рубль 200\n\
\nЧтобы увидеть список доступных валют набери команду /values\nили просто нажми на неё'
    bot.reply_to(message, text)

@bot.message_handler(commands = ['values'])
def values(message):
    text = 'Доступные валюты:\n'
    for key in keys.keys():
        text = '\n'.join((text, key, ))
    bot.reply_to(message, text)


@bot.message_handler(content_types = ['text', ])
def convert(message):
    try:
        values = message.text.split(' ')

        if len(values) != 3:
            raise ConvertionException('Задано неверное количество параметров')

        quote, base, amount = values

        total_base = CryptoConverter.convert(quote, base, amount)
        total_base = round(total_base * float(amount), 2)
    except ConvertionException as e:
        bot.reply_to(message, f'Ошибка пользователя\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать запрос\n{e}')
    else:
        text = f'Цена {amount} {quote} будет равна {total_base} {base}'
        bot.send_message(message.chat.id, text)


bot.polling()

