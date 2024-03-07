import telebot
from  telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
import requests
import json
from unidecode import unidecode
Telegram_Api = '6888394615:AAFI3VNXrw4xtOxfxUUTlXEkTBm2I7QW3og'
bot = telebot.TeleBot(Telegram_Api)
bot_activado = True
ContrasenaG = 1012020


@bot.message_handler(func=lambda message: True)
def on_any_message(message):
    global bot_activado
    if bot_activado:
        markup = InlineKeyboardMarkup(row_width=2)
        item1 = InlineKeyboardButton('Si, deseo crear una cuenta', callback_data='Si1')
        item2 = InlineKeyboardButton("No en este momento", callback_data="later")
        markup.add(item1, item2)
        bot.reply_to(message.chat.id, '¡Hola! Soy InventarioHardware, tu bot para conocer el inventario. ¿Deseas crear una cuenta?', reply_markup=markup)
        bot_activado = False


    
@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data == 'Si1':
        bot.send_message(call.message.chat.id, "Por favor ingresa tu Nombre:")
        bot.register_next_step_handler(call.message, guardar_nombre)
    elif call.data == 'later':
        Regresar(call.message)

def guardar_nombre(message):
    global name
    name = message.text
    name = unidecode(name)
    bot.send_message(message.chat.id, "Ahora ingresa tu Apellido:")
    bot.register_next_step_handler(message, guardar_apellido)

def guardar_apellido(message):
    global lastname
    lastname = message.text
    lastname = unidecode(lastname)
    bot.send_message(message.chat.id, "Por favor ingresa tu Contraseña:")
    bot.register_next_step_handler(message, lambda msg: validar_contrasena(msg, name))



def Regresar(message):
     global bot_activado
     bot.send_message(message.chat.id,"!Listo si me vuelves a necesitar, no dudes en escribirme")
     bot_activado = False

def validar_contrasena(message, name):
    global Contra
    Contra = message.text
    Contra = unidecode(Contra)
    if int(ContrasenaG) == int(Contra):  # Comparar la contraseña con ContrasenaG
        bot.send_message(message.chat.id, '¡Contraseña Correcta!')
        telegram_id = message.chat.id  # Obtener automáticamente el ID de Telegram del usuario
        guardar_datos_en_archivo(name, lastname, telegram_id)  # Guardar los datos en el archivo directamente
        bot.send_message(message.chat.id, '¡Tus datos se han guardado correctamente!')
    else:
        bot.send_message(message.chat.id, "¡Contraseña incorrecta! Por favor intenta nuevamente.")
        bot.register_next_step_handler(message, guardar_apellido)  # Volver a solicitar la contraseña

def guardar_datos_en_archivo(name, lastname, telegram_id):
    with open('usuarios.txt', 'w') as file:
        file.write(f"Nombre: {lastname}\n")  # Cambio de name a lastname
        file.write(f"Apellido: {name}\n")    # Cambio de lastname a name
        file.write(f"ID de Telegram: {telegram_id}\n")
        file.write("\n")




bot.polling()





