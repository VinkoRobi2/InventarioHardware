# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import font
import os
import cv2
from PIL import Image
from opencv.fr import FR
from opencv.fr.search.schemas import SearchRequest, SearchMode
import json
import pygame
import time
import threading
import telebot
import requests
from telebot import types
from opencv.fr.persons.schemas import PersonBase
from pathlib import Path
from openai import OpenAI
import evdev
import random
from unidecode import unidecode


client = OpenAI(api_key="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")
BACKEND_URL="https://us.opencv.fr"
DEVELOPER_KEY="eUKiJNuMTAzZWY3ZjEtMzliZi00ZjRjLWIzYTUtYmU4YmZhNTA1OWI2"

sdk= FR(
  BACKEND_URL,
  DEVELOPER_KEY
  )


TOKEN = "7085496526:AAFVvFC-6BiJcm_WUBPnLcQVWwezk8e9oP0"
bot = telebot.TeleBot(TOKEN)


def telegram_bot():
  userspath = "/home/katukstore/Documents/bd/usuarios.txt" 
  def user_exists(user_id):
      global idtelegram
      with open(userspath, "r") as archivo:
          datos = archivo.readlines()
      for line in datos:
          if str(user_id) in line:
              idtelegram = user_id
              return True
      return False
  
  def guardar_nombre(message):#Terminado
      global name
      name = message.text
      name=unidecode(name)
      bot.send_message(message.chat.id, "Ahora ingresa tu apellido :")
      bot.register_next_step_handler(message, guardar_apellido)
      
  def guardar_apellido(message):#Terminado
      global lastname
      lastname = message.text
      lastname=unidecode(lastname)
      bot.send_message(message.chat.id, "Ahora envía tu numero de celular:")
      bot.register_next_step_handler(message, guardar_celular)
      
  def guardar_celular(message):#Terminado
      global celular
      celular = message.text
      bot.send_message(message.chat.id, "Ahora envía una selfie tuya:")
      bot.register_next_step_handler(message, guardar_foto)
      
      
  def guardar_foto(message):
      bot.send_message(message.chat.id, "¡Gracias! Por favor, espere unos segundos mientras procesamos su imagen.")
      user_id = message.from_user.id
      idtelegram= user_id
      ruta="/home/katukstore/Documents/bd/usuarios/"
      nombre = name + " " + lastname
      with open(userspath, "r") as archivo:
        datos = json.load(archivo)
      nuevo_usuario = {"telegram": idtelegram, "telefono": celular,"usuario":nombre}
      datos.append(nuevo_usuario)
      with open(userspath, "w") as archivo:
        json.dump(datos, archivo)
      lista=["Propietario","Whitelist","Blacklist","Propietario/photo","Propietario/voice","Whitelist/voice","Blacklist/voice","Whitelist/photo","Blacklist/photo"]
      for directorio in lista:
        path=nombre+"/"+directorio
        propietariopath=ruta+path
        print(propietariopath)
        if not os.path.exists(propietariopath):
          os.makedirs(propietariopath)
      photo_info = bot.get_file(message.photo[-1].file_id)
      photo_path = photo_info.file_path
      photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{photo_path}"
      response = requests.get(photo_url)
      photo_address= "/home/katukstore/Documents/bd/usuarios/"+nombre+"/Propietario/photo/"+f"{name}_{lastname}.jpg"
      if os.path.exists(photo_address):
          print("La ruta existe en tu Raspberry Pi.")
      else:
          with open(photo_address, "wb") as photo_file:
              photo_file.write(response.content)
           
          person = PersonBase(
              [
                photo_address,
              ],
              name=nombre
            )          
          person =sdk.persons.create(person)
          
      categoria="Propietario"
      audio_path = "/home/katukstore/Documents/bd/usuarios/"+nombre+"/Propietario/voice/"+nombre + ".mp3"    
      if os.path.exists(audio_path):
          print("La ruta existe en tu Raspberry Pi.")
      else:
          print("No existe audio")
          mensaje = "Bienvenido" + "  " + nombre  
          response = client.audio.speech.create(
              model="tts-1",
              voice="nova",
              speed="1.00",
              input=mensaje 
            )            
          response.stream_to_file(audio_path)
      txtpath="/home/katukstore/Documents/bd/usuarios/"+nombre+"/Propietario/info.txt"  
      nuevo_elemento = {
          "telegram": idtelegram,
          "nombre": nombre,
          "foto": photo_address,
          "voz": audio_path,
          "categoria": categoria
          }
      contenido = json.dumps(nuevo_elemento)
  
      with open(txtpath, "w") as archivo:
        archivo.write(contenido)
      keyboard = types.InlineKeyboardMarkup()
      button_menu = types.InlineKeyboardButton(text="Continuar al menú.", callback_data="menu")
      button_exit = types.InlineKeyboardButton(text="Salir", callback_data="exit")       
      keyboard.row(button_menu)
      keyboard.row(button_exit)       
      bot.send_message(message.chat.id, "¡Cuenta creada exitosamente! ¿Qué deseas hacer? Puedes continuar al menú o salir.", reply_markup=keyboard)
      
  def recibir_datos(message):#Terminado
      global nameWhitelist
      nameWhitelist = message.text
      nameWhitelist=unidecode(nameWhitelist)
      bot.send_message(message.chat.id, "Ahora ingresa el apellido:")
      bot.register_next_step_handler(message, recibir_apellido)
      
  def recibir_apellido(message):#Terminado
      global lastnameWhitelist
      lastnameWhitelist = message.text
      lastnameWhitelist=unidecode(lastnameWhitelist)
      bot.send_message(message.chat.id, "Ahora ingresa el celular:")
      bot.register_next_step_handler(message, recibir_celular)
      
  def recibir_celular(message):#Terminado
      global celularWhitelist
      celularWhitelist = message.text
      bot.send_message(message.chat.id, "Ahora envía una foto de la persona que deseas agregar:")
      bot.register_next_step_handler(message, recibir_foto)
      
  def recibir_foto(message):#terminado
      bot.send_message(message.chat.id, "¡Gracias! Por favor, espere unos segundos mientras procesamos su imagen.")
      user_id = message.from_user.id
      with open("/home/katukstore/Documents/bd/usuarios.txt", 'r') as file:
        data = json.load(file)
      for item in data:
        if item['telegram'] == user_id:
            propietario = item['usuario']
            break
      nombreWhitelist = nameWhitelist + " " + lastnameWhitelist
      photo_info = bot.get_file(message.photo[-1].file_id)
      photo_path = photo_info.file_path
      photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{photo_path}"
      response = requests.get(photo_url)
      photo_address= "/home/katukstore/Documents/bd/usuarios/"+propietario+"/Whitelist/photo/" + f"{nameWhitelist}_{lastnameWhitelist}.jpg"
      if os.path.exists(photo_address):
          print("La ruta existe en tu Raspberry Pi.")
      else:
          with open(photo_address, "wb") as photo_file:
              photo_file.write(response.content)
            
          person = PersonBase(
              [
                photo_address,
              ],
              name=nombreWhitelist
            )          
          person = sdk.persons.create(person)
          
          categoria="Whitelist"
          audio_path = "/home/katukstore/Documents/bd/usuarios/"+propietario+"/Whitelist/voice/"+nombreWhitelist + ".mp3"
          
      if os.path.exists(audio_path):
          print("La ruta existe en tu Raspberry Pi.")
      else:
          mensaje = "Bienvenido" + "  " + nombreWhitelist+" ."+ "Usuario Autorizado" 
          response = client.audio.speech.create(
              model="tts-1",
              voice="nova",
              speed="1.00",
              input=mensaje 
            )            
          response.stream_to_file(audio_path)
      
      nuevo_elemento = {
        "nombre": nombreWhitelist,
        "foto": photo_address,
        "voz": audio_path,
        "celular":celularWhitelist,
        "categoria": categoria
        }
      txtWhitelistpath="/home/katukstore/Documents/bd/usuarios/"+propietario+"/Whitelist/info.txt"
          
      if os.path.exists(txtWhitelistpath):
        with open(txtWhitelistpath, "r") as archivo:
            contenido = json.load(archivo)
        contenido.append(nuevo_elemento)
      else:
        contenido = [nuevo_elemento]
      with open(txtWhitelistpath, "w") as archivo:
          json.dump(contenido, archivo)
      
      keyboard = types.InlineKeyboardMarkup()
      button_menu = types.InlineKeyboardButton(text="Continuar al menú.", callback_data="menu")
      button_exit = types.InlineKeyboardButton(text="Salir", callback_data="exit")       
      keyboard.row(button_menu)
      keyboard.row(button_exit)       
      bot.send_message(message.chat.id, "¡Usuario agregado a la Whitelist! ¿Deseas volver al menu?.", reply_markup=keyboard)
      
  def recibir_datosBlacklist(message):
      global nameBlacklist
      nameBlacklist = message.text
      nameBlacklist=unidecode(nameBlacklist)
      bot.send_message(message.chat.id, "Ahora ingresa el apellido:")
      bot.register_next_step_handler(message, recibir_apellidoBacklist)
      
  def recibir_apellidoBacklist(message):
      global lastnameBlacklist
      lastnameBlacklist = message.text
      lastnameBlacklist=unidecode(lastnameBlacklist)
      bot.send_message(message.chat.id, "Ahora envía una foto de la persona que deseas agregar:")
      bot.register_next_step_handler(message, recibir_fotoBlacklist)
      
  def recibir_fotoBlacklist(message):
      bot.send_message(message.chat.id, "¡Gracias! Por favor, espere unos segundos mientras procesamos su imagen.")
      user_id = message.from_user.id
      with open("/home/katukstore/Documents/bd/usuarios.txt", 'r') as file:
        data = json.load(file)
      for item in data:
        if item['telegram'] == user_id:
            propietario = item['usuario']
            break
      nombreBlacklist = nameBlacklist + " " + lastnameBlacklist
      photo_info = bot.get_file(message.photo[-1].file_id)
      photo_path = photo_info.file_path
      photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{photo_path}"
      response = requests.get(photo_url)
      photo_address= "/home/katukstore/Documents/bd/usuarios/"+propietario+"/Blacklist/photo/" + f"{nameBlacklist}_{lastnameBlacklist}.jpg"
      if os.path.exists(photo_address):
          print("La ruta existe en tu Raspberry Pi.")
      else:
          with open(photo_address, "wb") as photo_file:
              photo_file.write(response.content)
            
          person = PersonBase(
              [
                photo_address,
              ],
              name=nombreBlacklist
            )          
          person = sdk.persons.create(person)
          
      categoria="Blacklist"
      audio_path = "/home/katukstore/Documents/bd/usuarios/"+propietario+"/Blacklist/voice/"+ nombreBlacklist + ".mp3"
          
      if os.path.exists(audio_path):
          print("La ruta existe en tu Raspberry Pi.")
      else:
          mensaje = "Usuario No Autorizado." 
          response = client.audio.speech.create(
              model="tts-1",
              voice="nova",
              speed="1.00",
              input=mensaje 
            )            
          response.stream_to_file(audio_path)
            
      nuevo_elemento = {
        "nombre": nombreBlacklist,
        "foto": photo_address,
        "voz": audio_path,
        "categoria": categoria
        }
      txtBlackpath="/home/katukstore/Documents/bd/usuarios/"+propietario+"/Blacklist/info.txt"
          
      if os.path.exists(txtBlackpath):
        with open(txtBlackpath, "r") as archivo:
            contenido = json.load(archivo)
        contenido.append(nuevo_elemento)
      else:
        contenido = [nuevo_elemento]
      with open(txtBlackpath, "w") as archivo:
          json.dump(contenido, archivo)
      
      keyboard = types.InlineKeyboardMarkup()
      button_menu = types.InlineKeyboardButton(text="Continuar al menú.", callback_data="menu")
      button_exit = types.InlineKeyboardButton(text="Salir", callback_data="exit")       
      keyboard.row(button_menu)
      keyboard.row(button_exit)       
      bot.send_message(message.chat.id, "¡Usuario agregado a la Blacklist! ¿Deseas volver al menu?.", reply_markup=keyboard)     
  
  
  def generar_numero_aleatorio():
      return str(random.randint(1000, 9999))
  
  def obtener_nombre_celular(json_file):
      with open(json_file, 'r') as file:
          data = json.load(file)
      return [(item["nombre"], item["celular"]) for item in data]
  
  def obtener_telegram_from_celular(celular):
      with open("/home/katukstore/Documents/bd/usuarios.txt", 'r') as file:
          data = json.load(file)
      for item in data:
        if item["telefono"]==celular:
          break
      return item["telegram"]
  
  def construir_botones(lista_personas):
      keyboard = types.InlineKeyboardMarkup()
      for nombre, celular in lista_personas:
          texto_boton = f"{nombre} - {celular}"
          callback_data = f"verificar_{celular}"
          button = types.InlineKeyboardButton(text=texto_boton, callback_data=callback_data)
          keyboard.row(button)
      return keyboard
  
  def handle_callback_verificar(call):
      global numero_aleatorio
      user_id = call.message.chat.id
      with open("/home/katukstore/Documents/bd/usuarios.txt", 'r') as file:
        data = json.load(file)
      for item in data:
        if item['telegram'] == user_id:
          propietario = item['usuario']
          break
      path="/home/katukstore/Documents/bd/usuarios/"+propietario+"/Whitelist/info.txt"
      celular = call.data.split("_")[1]
      with open(path, 'r') as file:
        data = json.load(file)
      for item in data:
        if item["celular"]==celular:
          nombre=item["nombre"]
      telegram = str(obtener_telegram_from_celular(celular))
      numero_aleatorio = generar_numero_aleatorio()
      mensaje = propietario+" "+"te envio un efectivo móvil."+" "+f"El código de seguridad es {numero_aleatorio}."
      bot.send_message(telegram, mensaje)
      
      with open("/home/katukstore/Documents/bd/codigos.txt", "r") as archivo:
        datos = json.load(archivo)       
      nuevo_elemento = {
        "codigo": numero_aleatorio,
        "telegram":user_id,
        "nombre":nombre
      }        
      datos.append(nuevo_elemento)
      with open("/home/katukstore/Documents/bd/codigos.txt", "w") as archivo:
        json.dump(datos, archivo)
  
          
          
  def send_welcome(message):
      keyboard = types.InlineKeyboardMarkup()
      button_yes = types.InlineKeyboardButton(text="Sí, crear cuenta", callback_data="create_account")
      button_no = types.InlineKeyboardButton(text="No, gracias", callback_data="no_account")
      keyboard.row(button_yes, button_no)
      bot.send_message(message.chat.id, "¡Hola! Soy Safy, tu asistente virtual de R&D. ¿Deseas crear una cuenta?", reply_markup=keyboard)
  
  def user_recognize(message, user_id):
      with open(userspath, 'r') as file:
          data = json.load(file)
      for item in data:
          if item['telegram'] == idtelegram:
              usuario = item['usuario']
              keyboard = types.InlineKeyboardMarkup()
              button_efectivo = types.InlineKeyboardButton(text="Efectivo móvil", callback_data="efectivo")
              button_add_whitelist = types.InlineKeyboardButton(text="Añadir a Whitelist", callback_data="add_whitelist")
              button_add_blacklist = types.InlineKeyboardButton(text="Añadir a Blacklist", callback_data="add_blacklist")
              button_view_whitelist = types.InlineKeyboardButton(text="Ver Whitelist", callback_data="view_whitelist")
              button_view_blacklist = types.InlineKeyboardButton(text="Ver Blacklist", callback_data="view_blacklist")
              button_exit = types.InlineKeyboardButton(text="Salir", callback_data="exit")
              
              keyboard.row(button_efectivo)
              keyboard.row(button_add_whitelist)
              keyboard.row(button_add_blacklist)
              keyboard.row(button_view_whitelist)
              keyboard.row(button_view_blacklist)
              keyboard.row(button_exit)
              
              bot.send_message(message.chat.id, f"Bienvenido de vuelta, {usuario}! ¿Qué deseas hacer?", reply_markup=keyboard)
              return
      send_welcome(message)
  
  
  @bot.message_handler(func=lambda message: True)
  def handle_message(message):
      global user_id
      user_id = message.from_user.id
      if user_exists(user_id):
          user_recognize(message, user_id)
      else:
          send_welcome(message)
  
 
  @bot.callback_query_handler(func=lambda call: True)
  def handle_callback(call):
      if call.data == "create_account":
          bot.send_message(call.message.chat.id, "¡Perfecto! Vamos a comenzar el proceso de creación de cuenta.")
          bot.send_message(call.message.chat.id, "Por favor, ingresa tu nombre:")
          bot.register_next_step_handler(call.message, guardar_nombre)
      elif call.data == "no_account":
          bot.send_message(call.message.chat.id, "Entiendo. Si cambias de opinión, siempre puedes volver y crear una cuenta más tarde.")
      elif call.data=="menu":
          keyboard = types.InlineKeyboardMarkup()
          button_efectivo = types.InlineKeyboardButton(text="Efectivo móvil", callback_data="efectivo")
          button_add_whitelist = types.InlineKeyboardButton(text="Añadir a Whitelist", callback_data="add_whitelist")
          button_add_blacklist = types.InlineKeyboardButton(text="Añadir a Blacklist", callback_data="add_blacklist")
          button_view_whitelist = types.InlineKeyboardButton(text="Ver Whitelist", callback_data="view_whitelist")
          button_view_blacklist = types.InlineKeyboardButton(text="Ver Blacklist", callback_data="view_blacklist")
          button_exit = types.InlineKeyboardButton(text="Salir", callback_data="exit")
              
          keyboard.row(button_efectivo)
          keyboard.row(button_add_whitelist)
          keyboard.row(button_add_blacklist)
          keyboard.row(button_view_whitelist)
          keyboard.row(button_view_blacklist)
          keyboard.row(button_exit)
              
          bot.send_message(call.message.chat.id," ¿Qué deseas hacer?", reply_markup=keyboard)
      
      elif call.data == "efectivo":
        user_id = call.message.chat.id
        with open("/home/katukstore/Documents/bd/usuarios.txt", 'r') as file:
          data = json.load(file)
          for item in data:
            if item['telegram'] == user_id:
              propietario = item['usuario']
              break
        searchpath="/home/katukstore/Documents/bd/usuarios/"+propietario+"/Whitelist/photo/"
        archivos = os.listdir(searchpath)
        cantidad_archivos = len(archivos)
        if cantidad_archivos > 0:
          lista_personas = obtener_nombre_celular("/home/katukstore/Documents/bd/usuarios/"+propietario+"/Whitelist/info.txt")
          keyboard = construir_botones(lista_personas)
          bot.send_message(call.message.chat.id, "A quien desea enviar el efectivo movil?", reply_markup=keyboard)
        else:
          keyboard = types.InlineKeyboardMarkup()
          button_menu = types.InlineKeyboardButton(text="Continuar al menú.", callback_data="menu")
          button_exit = types.InlineKeyboardButton(text="Salir", callback_data="exit")       
          keyboard.row(button_menu)
          keyboard.row(button_exit)       
          bot.send_message(call.message.chat.id, "Actualmente no tienes ningún usuario dentro de tu Whitelist para poder realizar un efectivo móvil.¡Pero no te preocupes! Puedes agregar usuarios desde el menu. ¿Deseas volver al menu?.", reply_markup=keyboard)
        
      elif call.data.startswith("verificar"):
          handle_callback_verificar(call)
          keyboard = types.InlineKeyboardMarkup()
          button_menu = types.InlineKeyboardButton(text="Regresar al menú.", callback_data="menu")
          button_exit = types.InlineKeyboardButton(text="Salir", callback_data="exit")       
          keyboard.row(button_menu)
          keyboard.row(button_exit)       
          bot.send_message(call.message.chat.id, "Efectivo movil enviado,"+f"El codigo de seguridad es {numero_aleatorio} "+"¿Deseas volver al menu?",reply_markup=keyboard)
          
      elif call.data == "add_whitelist":
          bot.send_message(call.message.chat.id, "Por favor, ingresa el nombre de la persona que deseas agregar a tu Whitelist.")
          bot.register_next_step_handler(call.message, recibir_datos)
      elif call.data == "add_blacklist":
          bot.send_message(call.message.chat.id, "Por favor, ingresa el nombre de la persona que deseas agregar a tu Blacklist.")
          bot.register_next_step_handler(call.message, recibir_datosBlacklist)
      elif call.data == "view_whitelist":
          user_id = call.message.chat.id
          with open("/home/katukstore/Documents/bd/usuarios.txt", 'r') as file:
            data = json.load(file)
          for item in data:
            if item['telegram'] == user_id:
              propietario = item['usuario']
              break
          searchpath="/home/katukstore/Documents/bd/usuarios/"+propietario+"/Whitelist/photo/"
          archivos = os.listdir(searchpath)
          cantidad_archivos = len(archivos)
          if cantidad_archivos > 0:
            bot.send_message(call.message.chat.id, "Los usuarios dentro de tu Whitelist son:\n")
            with open(("/home/katukstore/Documents/bd/usuarios/"+propietario+"/Whitelist/info.txt"), 'r') as file:
                  listaWhite = json.load(file)
            for item in listaWhite:
                nombre = item["nombre"]
                celular = item.get("celular", "No especificado")
                bot.send_message(call.message.chat.id, f"{nombre} - {celular}\n")
                              
            keyboard = types.InlineKeyboardMarkup()
            button_menu = types.InlineKeyboardButton(text="Regresar al menú.", callback_data="menu")
            button_exit = types.InlineKeyboardButton(text="Salir", callback_data="exit")       
            keyboard.row(button_menu)
            keyboard.row(button_exit)       
            bot.send_message(call.message.chat.id, "¿Deseas volver al menu?",reply_markup=keyboard)
          else:
            keyboard = types.InlineKeyboardMarkup()
            button_menu = types.InlineKeyboardButton(text="Regresar al menú.", callback_data="menu")
            button_exit = types.InlineKeyboardButton(text="Salir", callback_data="exit")       
            keyboard.row(button_menu)
            keyboard.row(button_exit)       
            bot.send_message(call.message.chat.id, "Actualmente no tienes ningún usuario dentro de tu Whitelist. ¡Pero no te preocupes! Puedes agregar usuarios desde el menu. ¿Deseas volver al menu? ",reply_markup=keyboard)
      
      elif call.data == "view_blacklist":
          user_id = call.message.chat.id
          with open("/home/katukstore/Documents/bd/usuarios.txt", 'r') as file:
            data = json.load(file)
          for item in data:
            if item['telegram'] == user_id:
              propietario = item['usuario']
              break
          searchpath="/home/katukstore/Documents/bd/usuarios/"+propietario+"/Blacklist/photo/"
          archivos = os.listdir(searchpath)
          cantidad_archivos = len(archivos)
          if cantidad_archivos > 0:
            bot.send_message(call.message.chat.id, "Los usuarios dentro de tu Blacklist son:\n")
            with open(("/home/katukstore/Documents/bd/usuarios/"+propietario+"/Blacklist/info.txt"), 'r') as file:
                  listaBlack = json.load(file)
            for item in listaBlack:
              nombre = item["nombre"]
              bot.send_message(call.message.chat.id, f"{nombre} - No Autorizado\n")
                              
            keyboard = types.InlineKeyboardMarkup()
            button_menu = types.InlineKeyboardButton(text="Regresar al menú.", callback_data="menu")
            button_exit = types.InlineKeyboardButton(text="Salir", callback_data="exit")       
            keyboard.row(button_menu)
            keyboard.row(button_exit)       
            bot.send_message(call.message.chat.id, "¿Deseas volver al menu?",reply_markup=keyboard)
          else:
            keyboard = types.InlineKeyboardMarkup()
            button_menu = types.InlineKeyboardButton(text="Regresar al menú.", callback_data="menu")
            button_exit = types.InlineKeyboardButton(text="Salir", callback_data="exit")       
            keyboard.row(button_menu)
            keyboard.row(button_exit)       
            bot.send_message(call.message.chat.id, "Actualmente no tienes ningún usuario dentro de tu Blacklist. ¡Pero no te preocupes! Puedes agregar usuarios desde el menu. ¿Deseas volver al menu? ",reply_markup=keyboard)
      elif call.data == "exit":
          bot.send_message(call.message.chat.id, "Gracias por tu interés. Recuerda que siempre eres bienvenido a volver cuando lo desees. ¡Hasta luego!")
  
  bot.polling()