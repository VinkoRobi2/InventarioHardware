import telebot
from  telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
import requests
from telebot import types
import json
Telegram_Api = '6888394615:AAFI3VNXrw4xtOxfxUUTlXEkTBm2I7QW3og'
bot = telebot.TeleBot(Telegram_Api)
bot_activado = True
ContrasenaG = 1012020
path = 'usuarios.txt'
pathC = 'categorias.txt'



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
    if call.data.startswith('verificar_'):
        categoria = call.data.split('_')[1]
        enviar_items(call, categoria)
    elif call.data == 'Salir':
        Regresar(call.message)
    elif call.data == 'VerLista':
        BotonesCategoria(call)
    elif call.data in categorias: 
        enviar_items(call, call.data) 


def guardar_nombre(message):
    global name
    name = message.text
    name = (name)
    bot.send_message(message.chat.id, "Ahora ingresa tu Apellido:")
    bot.register_next_step_handler(message, guardar_apellido)


def cargar_categorias():
    with open(pathC, 'r') as file:
        categorias_data = json.load(file)
        return categorias_data.get('categorias', {})

categorias = cargar_categorias()
print(categorias)

def obtener_items_por_categoria(categoria):
    items = cargar_items()
    return items.get('categorias', {}).get(categoria, [])



def enviar_items(call, categoria):
    items = obtener_items_por_categoria(categoria)
    if items:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for item in items:
            texto_boton = item['nombre']
            callback_data = f"verificar_item_{item['nombre']}"
            button = types.InlineKeyboardButton(text=texto_boton, callback_data=callback_data)
            keyboard.add(button)
        button_salir = types.InlineKeyboardButton(text="Salir", callback_data="Salir")
        keyboard.add(button_salir)
        bot.send_message(call.message.chat.id, f"Items para la categoría {categoria}:", reply_markup=keyboard)
    else:
        bot.send_message(call.message.chat.id, f"No hay items para la categoría {categoria}")



def cargar_items():
    with open(pathC, 'r') as file:
        items_data = json.load(file)
        return items_data


def construir_botones_categorias():
    categorias_lista = list(categorias.items())
    categorias_por_pares = [categorias_lista[i:i+2] for i in range(0, len(categorias_lista), 2)]

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for categoria_par in categorias_por_pares:
        buttons = []
        for categoria in categoria_par:
            nombre_categoria = categoria[0]
            button = types.InlineKeyboardButton(text=nombre_categoria, callback_data=nombre_categoria)
            buttons.append(button)
        keyboard.add(*buttons)
    
    return keyboard

def BotonesCategoria(call):
    keyboard = construir_botones_categorias()
    bot.send_message(call.message.chat.id, "Botones para todas las categorías:", reply_markup=keyboard)







def guardar_apellido(message):
    global lastname
    lastname = message.text
    lastname = (lastname)
    bot.send_message(message.chat.id, "Por favor ingresa tu Contraseña:")
    bot.register_next_step_handler(message, lambda msg: validar_contrasena(msg, name))



def Regresar(message):
     global bot_activado
     bot.send_message(message.chat.id,"!Listo si me vuelves a necesitar, no dudes en escribirme")
     bot_activado = True



def validar_contrasena(message, name):
    global Contra
    global telegram_id
    Contra = message.text
    Contra = (Contra)
    if int(ContrasenaG) == int(Contra):  
        bot.send_message(message.chat.id, '¡Contraseña Correcta!')
        telegram_id = message.chat.id  
        guardar_datos_en_archivo(name, lastname, telegram_id)  
        bot.send_message(message.chat.id, '¡Tus datos se han guardado correctamente!')
        Opciones(message)
    else:
        bot.send_message(message.chat.id, "¡Contraseña incorrecta! Por favor intenta nuevamente.")
        bot.register_next_step_handler(message, guardar_apellido)  




def guardar_datos_en_archivo(name, lastname, telegram_id):
    with open(path, "r+") as archivo:
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
    global markup
    markup = InlineKeyboardMarkup(row_width=1)
    item1 = InlineKeyboardButton('Ver Lista',callback_data='VerLista')
    item3 = InlineKeyboardButton('Agregar Categoria', callback_data='AgregarCategoria')
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
        with open(path, "r") as archivo:
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
