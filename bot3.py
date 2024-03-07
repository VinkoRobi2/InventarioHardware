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
    telegram_id = message.from_user.id
    if user_exists(telegram_id):
        user_recognize(message, telegram_id)
    else:
        global bot_activado
        if bot_activado:
            markup = InlineKeyboardMarkup(row_width=2)
            item1 = InlineKeyboardButton('Si, deseo crear una cuenta', callback_data='Si1')
            item2 = InlineKeyboardButton("No en este momento", callback_data="later")
            markup.add(item1, item2)
            bot.reply_to(message, '¡Hola! Soy InventarioHardware, tu bot para conocer el inventario. ¿Deseas crear una cuenta?', reply_markup=markup)
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
    global telegram_id
    Contra = message.text
    Contra = unidecode(Contra)
    if int(ContrasenaG) == int(Contra):  
        bot.send_message(message.chat.id, '¡Contraseña Correcta!')
        telegram_id = message.chat.id  
        guardar_datos_en_archivo(name, lastname, telegram_id)  
        bot.send_message(message.chat.id, '¡Tus datos se han guardado correctamente!')
    else:
        bot.send_message(message.chat.id, "¡Contraseña incorrecta! Por favor intenta nuevamente.")
        bot.register_next_step_handler(message, guardar_apellido)  




def guardar_datos_en_archivo(name, lastname, telegram_id):
    with open("usuarios.txt", "r+") as archivo:
        datos = json.load(archivo)       
        nuevo_elemento = {
            "Apellido": lastname,
            "telegram": telegram_id,
            "Nombre": name
        }        
        datos.append(nuevo_elemento)
        archivo.seek(0)  
        json.dump(datos, archivo, indent=4)  
    usuarios.clear()  
    usuarios.extend(datos) 




def Opciones(message):
    markup = InlineKeyboardMarkup(row_width=1)
    item1 = InlineKeyboardButton('Ver Lista',callback_data='VerLista')
    item3 = InlineKeyboardButton('Agregar Item', callback_data='AgregarItem')
    item4 = InlineKeyboardButton('Eliminar Item', callback_data='EliminarItem')
    item2 = InlineKeyboardButton('Salir', callback_data='Salir')
    markup.add(item1,item3,item4,item2)
    for item in usuarios:
        if item['telegram'] == message.from_user.id:
            usuario = f"{item['Nombre']} {item['Apellido']}"
            mensaje = f"Bienvenido de vuelta, {usuario}! ¿Qué deseas hacer?"
            bot.send_message(message.chat.id, mensaje, reply_markup=markup)
            return

    bot.send_message(message.chat.id, '¡Bienvenido! ¿Deseas crear una cuenta?', reply_markup=markup)

var = []

@bot.callback_query_handler(func=lambda call:call.data == 'VerLista')

    


def user_recognize(message, telegram_id):
    for item in usuarios:
        if item['telegram'] == telegram_id:
            Opciones(message) 
            return
    on_any_message(message)



def user_exists(telegram_id):
    for item in usuarios:
        if item['telegram'] == telegram_id:
            return True
    return False




def cargar_usuarios():
    try:
        with open("usuarios.txt", "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []

usuarios = cargar_usuarios()







@bot.message_handler(func=lambda message: True)
def handle_message(message):
      
      telegram_id = message.from_user.id
      if user_exists(telegram_id):
          print(telegram_id)
          user_recognize(message, telegram_id)
      else:
          print(telegram_id)
          on_any_message(message)




bot.polling()







