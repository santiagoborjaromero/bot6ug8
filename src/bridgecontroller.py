import json
import os
from pprint import pprint
import re
import emoji

from src.controller import getDictionary, getSpelling, botAudit, setPassword, checkPassword, startSession, switchIAbot, capasNeuronales
from src.utils import logger
from src.redneuronal import analyzingTextRN

def sendMessage(bot, chat_id, text):
    bot.sendMessage(chat_id, text)
    return

def processing(content_type, msg, chat_type, chat_id, bot):
    module = "bridgeController.processing.RF."
    result_text = ""
    
    # *******************************
    # Valida si estan enviado Emojis
    # *******************************
    if emoji.emoji_count(msg["text"])>0:
        msg["text"] = emoji.replace_emoji(msg["text"],"")
    
    msg["text"] = msg["text"].strip()
    
    if (msg["text"] == ""):
        return 
    
    sendMessage(bot, chat_id, "🕜 Procesando ...")
    logger("DEBUG", msg, f"{module}29")
    
    valid = validate(content_type, chat_type, msg,  bot, chat_id)
    if valid == False:
        return 
    
    # **************************************
    # Clasificando la informacion que llega
    # **************************************
    
    idUser = msg["from"]["id"]
    
    try:
        username = msg["from"]["username"]
    except Exception as err: 
        logger("ERROR", f"No tiene username, {err}", f"{module}52")
        username = ""
    
    try:
        author = msg["from"]["first_name"] + " " + msg["from"]["last_name"]
    except Exception as err: 
        logger("ERROR", err, f"{module}58")
        if username!='':
            author = username 
        else:
            author = "Usuario no Identificado"
            
    lang = msg["from"]["language_code"]
    
    # ************************************
    # Limpiando la informacion que llega
    # ************************************
    
    texto_original = msg["text"].lower()
    
    esMenu = texto_original[0]
    
    t = re.sub(r"[^a-z0-9 _,]", "", texto_original)
    t = re.sub(r"[ ]", ",", t)
    
    texto_depurado = re.sub(r",", " ", t)
    texto_array = t.split(",")
    
    # *******************************
    # revisar si es opcion del menu
    # *******************************
    
    if (esMenu == "/"):
        resp = getDictionary(texto_array[0], len(texto_array), texto_array, author, idUser, bot, chat_id, "db")
        sendMessage(bot, chat_id, resp)
        return 
    
    # ***********************
    # validando informacion 
    # ***********************
    
    if texto_array[0] in ["password", "checkpassword", "login"]:
        checkFirstActions(bot, chat_id, idUser, author, texto_array)
        return 
        
    rbot = switchIAbot()
    if (len(rbot) == 0):
        rbot = "db"

    modeBot = rbot
         
    logger("DEBUG", f"BOT MODE {modeBot}", f"{module}49")
    
    keyWord = ""

    if (modeBot == "redneuronal"):
        # gemini
        keyWord = analyzingTextRN(chat_id, bot, texto_depurado)
    else:
        # Solo para DB
        keyWord = getSpelling(texto_array)
    
    result = botAudit(idUser, author, lang, username, texto_depurado, keyWord, json.dumps(msg))
    print("botAudit", result)
    desicion = checkAuditResult(bot, chat_id, author, result)
    if desicion == False:
        return
    
    if keyWord  == "":
        result_text = "Lo siento " + author + ", no he comprendido lo que solicitas, nececitas mas ayuda?\n\n/ayuda - Despliega las opciones de ayuda\n/menu - Muestra las opciones del menu principal."
    else:
        result_text = getDictionary(keyWord, len(texto_array), texto_array, author, idUser, bot, chat_id, modeBot)

    # bot.sendMessage(chat_id, result_text)
    sendMessage(bot, chat_id, result_text)
    
    checkTemps()



def checkTemps():
    directorio = 'temp/'
    # contenido = os.listdir(directorio)
    try:
        with os.scandir(directorio) as ficheros:
            for fichero in ficheros:
                print(f"temp/{fichero.name}")
                os.remove(f"temp/{fichero.name}")
    except OSError as error:
        print(f"Error al eliminar el archivo: {error}")
                    


def checkAuditResult(bot, chat_id, author = '', result = None):
    
    print(result)
    
    if result != None:
        r = result[0]["sndRESPONSE"]
        ress = r.split("|")
        print(ress[0],ress[1])
    
        if (ress[0] == "NEW"):
            if ress[1] == "PASSWORD":
                result_text = "Eres nuev@ por aqui " + author + " , debes registrarte, " \
                    "por favor ingresa una contraseña, de la siguiente forma \n" \
                    "password AQUI_CONTRASEÑA."
                sendMessage(bot, chat_id, result_text)
            return False
        elif (ress[0] == "SET"):
            if ress[1] == "PASSWOOD":
                result_text = author + ", estamos validando las conexiones que no sea gente que nos puede hacer daño, tu entenderás, " \
                    "y vemos que no tienes establecida una clave personal, " \
                    "por favor ingresa una contraseña, de la siguiente forma \n" \
                    "password AQUI_CONTRASEÑA"
                sendMessage(bot, chat_id, result_text)
            return False
        elif (ress[0] == "LOGIN"):
            result_text = author + ", es importante registrarte como usuario valido por favor ingresa login y tu contraseña.\n" \
                "Por seguridad de todos se te soliucitara una vez al dia.\n" \
                "Por favor ingresa login y tu contraseña, de la siguiente forma \n" \
                "login AQUI_CONTRASEÑA"
            sendMessage(bot, chat_id, result_text)
            return False
    return True


def checkFirstActions(bot, chat_id, idUser, author, text):
    print(text)
    match text[0]:
        case "password":
            if (len(text) == 1):
                sendMessage(bot, chat_id, "❌ No establecio clave alguna. Para establecer o actualizar su clave o pin de usuario debe escribir\npassword <clave>")
                return
            
            if (text[1] == ""):
                sendMessage(bot, chat_id, "❌ No establecio clave alguna. Para establecer o actualizar su clave o pin de usuario debe escribir\npassword <clave>")
                return
                
            result_text = setPassword(idUser, text[1])
            print(result_text)
            ressetp = result_text.split("|")

            if ressetp[0] == "EXEC":
                textoO = "CHANGE PASSWORD"
                text = [ressetp[1]]
                sendMessage(bot, chat_id, "cambio de contraseña exitosamente")
            elif ressetp[0] == "ERROR":
                if ressetp[1] == "ERROR USUARIO NO ENCONTRADO":
                    result_text = "❌ Tenemos algunos problemas para encontrar tu usuario, podemos intentarlo nuevamente?"
                else:
                    result_text = ressetp[1]
                
                sendMessage(bot, chat_id, result_text)
                return
            return
        case "checkpassword":
            result_text = checkPassword(idUser)
            print(result_text)
            ressetp = result_text.split("|")
            if ressetp[0] == "SHOW":
                text = ressetp[1]
                sendMessage(bot, chat_id, "Su clave de acceso es: " + text + "\n\n/menu - Puedes regresar al menu principal.")
                return 
            elif ressetp[0] == "ERROR":
                if ressetp[1] == "ERROR USUARIO NO ENCONTRADO":
                    result_text = "❌ Tenemos algunos problemas para encontrar tu usuario, podemos intentarlo nuevamente?"
                else:
                    result_text = ressetp[1]
                
                sendMessage(bot, chat_id, result_text)
                return
            return
        case "login":
            result_text = startSession(idUser, text[1])
            print(result_text)
            ressetp = result_text.split("|")
            if ressetp[0] == "SHOW":
                text = ressetp[1]
                sendMessage(bot, chat_id, "Su clave de acceso es: " + text + "\n\n/menu - Puedes regresar al menu principal.")
                return 
            elif ressetp[0] == "ERROR":
                if ressetp[1] == "ERROR USUARIO NO ENCONTRADO":
                    result_text = "❌ Tenemos algunos problemas para encontrar tu usuario, podemos intentarlo nuevamente?"
                else:
                    result_text = ressetp[1]
                
                sendMessage(bot, chat_id, result_text)
                return
            return
        
        
        


def validate(content_type, chat_type, msg,  bot, chat_id):
    module = "bridgeController.validate.RF."
    if content_type != 'text':
        txtmsg = "🚫 Has enviado un archivo, por el momento no puedo procesarlo.\n" \
            "/menu - Para desplegar el listado de opciones del menú." \
            "/ayuda - Para saber mas de como puedes ingresar tus requerimientos."

        sendMessage(bot, chat_id, txtmsg)
        return False
    
    if chat_type != 'private':
        txtmsg = "🚫 El chat de donde escribes no es personal" \
            "/menu - Para desplegar el listado de opciones del menú." \
            "/ayuda - Para saber mas de como puedes ingresar tus requerimientos."
        sendMessage(bot, chat_id, txtmsg)
        return False
    
    is_bot = msg["from"]["is_bot"]
    if is_bot == True:
        logger("WARNING", "❌ Lo siento no eres humano.",  f"{module}101")
        sendMessage(bot, chat_id, "Lo siento no eres humano")
        return False
    
    return True
