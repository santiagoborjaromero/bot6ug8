import os
import json
import mysql.connector
from datetime import date, time, datetime
import numpy as np

from config.init import APIPATH
from pprint import pprint
from src.utils import logger, open_file
import requests
import json 

conn = None
cursor = None
apiPath = APIPATH
headers = {'user-agent': '6UG8Bot / 0.0.2', 'Content-type': 'application/json'}

def getApi(sql, args = None):
    params = {'sql':sql, "args": args}
    res = requests.get(apiPath, headers=headers, params=params)
    response = json.loads(res.text)
    return response

def switchIAbot():
    switchbot = "own"
    sqlcmd = "select vvalue from config WHERE variable = 'switch_ia_bot' "
    rows = getApi(sqlcmd)
    if (rows["status"]=="ok"):
        return rows["message"][0]["vvalue"]
    else:
        logger("ERROR", rows["message"], "CONTROLLER.LN.56")
            
    return ""
    
def capasNeuronales():
    sqlcmd = "SELECT wordfind as entrada, menurun as salida FROM bot_spelling WHERE confirmed = 1 "
    rows = getApi(sqlcmd)
    if (rows["status"]=="ok"):
        return rows["message"]
    else:
        logger("ERROR", rows["message"], "CONTROLLER.LN.70")
    return "ERROR"
        

def botAudit(idUser = 0, author = '',lang = 'es', username='', textentered = "", keyresult = '', bot = None):
    sqlcmd = f"CALL store_bot_messages ({idUser},'{author}','{lang}','{username}','{textentered}','{keyresult}',{json.dumps(bot)})"
    # print(sqlcmd)
    rows = getApi(sqlcmd)
    if (rows["status"]=="ok"):
        return rows["message"]
    else:
        logger("ERROR", rows, "CONTROLLER.LN.52")
    return "ERROR"


def startSession(idUser, currentpass):
    sqlcmd = f"CALL set_session('{idUser}', '{currentpass}')"
    rows = getApi(sqlcmd)
    if (rows["status"]=="ok"):
        return rows["message"]
    else:
        logger("ERROR", rows["message"], "CONTROLLER.LN.80")
    return "ERROR|EMPTY"
    
        # # print(sqlcmd)
        
        # msg = ""
        # with conn.cursor() as cursor:
        #     cursor.execute(sqlcmd, args)
        #     rows = cursor.fetchall()
            
        #     if len(rows) == 0:
        #         return "ERROR|EMPTY"
        
        #     for row in rows:
        #         msg = row[0]
        # return msg
    
def checkPassword(idUser):
    sqlcmd = "CALL check_password(" + str(idUser) + ")"
        
    rows = getApi(sqlcmd)
    if (rows["status"]=="ok"):
        return rows["message"]
    else:
        logger("ERROR", rows["message"], "CONTROLLER.LN.80")
    return "ERROR|EMPTY"
        
        # msg = ""
        # with conn.cursor() as cursor:
        #     cursor.execute(sqlcmd)
        #     rows = cursor.fetchall()
            
        #     if len(rows) == 0:
        #         return "ERROR|EMPTY"
        
        #     for row in rows:
        #         msg = row[0]
        # return msg
        
def setPassword(idUser, password):
    sqlcmd = f"CALL set_password ('{idUser}','{password}')"
    # args = (idUser, password)
    
    rows = getApi(sqlcmd)
    if (rows["status"]=="ok"):
        return rows["message"]
    else:
        logger("ERROR", rows["message"], "CONTROLLER.LN.80")
    return "Lista ya estas creado, gracias, ahora si a informarnos. Que necesitas saber?"
        
    # print(sqlcmd, args)
    
    # msg = ""
    # with conn.cursor() as cursor:
    #     cursor.execute(sqlcmd, args)
    #     rows = cursor.fetchall()
        
    #     if len(rows) == 0:
    #         return "ERROR|EMPTY"
    
    #     for row in rows:
    #         msg = row[0]
            
    # # conn.commit()   # solo se usa cuando hay insert
    # return msg
    
    
    # return "Lista ya estas creado, gracias, ahora si a informarnos. Que necesitas saber?"

def getSpelling(words):

    sqlcmd = "SELECT menurun from bot_spelling WHERE wordfind IN ("
    
    count = 0
    connc = ""
    
    for w in words:
        count = count + 1
        # sqlcmd = sqlcmd + " OR wordfind like '%" + w + "%'"
        if count>1:
            connc = ","
        else:
            connc = ""
            
        sqlcmd = sqlcmd + connc +  "'" + w + "'"
    
    sqlcmd = sqlcmd + ") LIMIT 1"
    
    rows = getApi(sqlcmd)
    if (rows["status"]=="ok"):
        return rows["message"]
    else:
        logger("ERROR", "Los datos no se encuentran disponibles por el momento, e04.", "CONTROLLER.LN.80")
    return "Los datos no se encuentran disponibles por el momento, e04."
    
    # try:
    #     cursor = conn.cursor()
    #     cursor.execute(sqlcmd)
    #     rows = cursor.fetchall()
        
    #     # pprint(rows)
        
    #     if len(rows) == 0:
    #         return ""
        
    #     for row in rows:
    #         return row[0]
                
    # except Exception as err:
    #     print(err)
    #     logger("ERROR", err, "CONTROLLER.LN.174")
    #     return "Los datos no se encuentran disponibles por el momento, e04."
    
        
def getDictionary(findText, largo, obj, author, idUser, bot, chat_id, modeBot):
    if findText == "":
        return
    textResult = ""
    
    ddate = datetime.now()
    
    fecha = ddate.strftime("%Y-%m-%d")
    
    hora = ddate.hour
    min = ddate.minute
    
    hora_completa  = ddate.strftime("%H:%M:%S")
    
    fecha_hora = f"{ddate.strftime("%Y%m%d_%H%M%S")}"
    
    tiempo = ""
    
    if (hora >= 0 and min>=0) and (hora <=11 and min <= 59):
        tiempo = "buenos dias"
    elif (hora >= 12 and min>=0) and (hora <=18 and min <= 29):
        tiempo = "buenas tardes"
    elif (hora >= 18 and min>=30) and (hora <=23 and min <= 59):
        tiempo = "buenas noches"
        
    sqlcmd = "SELECT action,txt,field_search, description from bot_dictionary WHERE menu='" + findText + "' AND deleted_at IS NULL LIMIT 1"
    resp = getApi(sqlcmd)
    

    if (resp["status"]=="ok"):
        rows = resp["message"]
        
        if len(rows) == 0:
            return "Lo siento " + author + ", no he comprendido lo que solicitas, necesitas mas ayuda?\n\n/ayuda - Despliega las opciones de ayuda\n/menu - Muestra las opciones del menu principal."
        
        row = []
        row.append(rows[0]["action"])
        row.append(rows[0]["txt"])
        
        try:
            row.append(rows[0]["find_search"])
        except Exception as err: 
            row.append("")
        
        description = rows[0]["description"]
        
        
        if row[0] == "T":
            textResult = row[1].replace("<nombre>", author) 
            textResult = textResult.replace("<tiempo>", tiempo) 
            textResult = textResult.replace("<fecha>", fecha) 
            textResult = textResult.replace("<time>", hora_completa) 
            return textResult
        elif row[0] == "Q":
            sqlcmd = row[1]
            if (largo > 1 and modeBot != "redneuronal"):
                if (obj!=""):
                    if (row[2]!=""):
                        sqlcmd = sqlcmd + " AND " + row[2] +  " LIKE '%" + obj[1] + "%'"
            
            respQ = getApi(sqlcmd)
            if (respQ["status"]=="ok"):
                
                rs = respQ["message"]
                if len(rs) == 0:
                    return "No existen registros de " + findText + ", se encuentra vacío. \n\n/menu - Muestra las opciones del menu principal."
            
                primerRegistro = rs[0]
                cols = []
                for key in primerRegistro:
                    cols.append(key)
                    
                columnas = ",".join(cols) + "\n"
                
                file_name = f"{findText}_{fecha_hora}.csv"
                
                f = open("temp/"+file_name, "w")
                f.write(columnas)
                
                for idx in range(len(rs)):
                    drow = []
                    for key in rs[idx]:
                        drow.append(rs[idx][key])
                        
                    filas = ",".join(drow) + "\n"
                    f.write(filas)
                    # data.append(",".join(drow) + "\n")s
                
                
                # f.write(filas)
                f.close()
                
                document = open("temp/"+file_name, "rb")
                
                bot.sendDocument(chat_id, document)
                    
                toSend = "Aqui la información solicitada. \n/menu - Regresar."
    
                return toSend 
            
            else:
                logger("ERROR", respQ["message"], "CONTROLLER.LN.273")
                return "ERROR"
            
        elif row[0] == "M":
            sqlcmd = row[1]
        
            if (largo > 1 and modeBot != "redneuronal"):
                if (obj!=""):
                    if (row[2]!=""):
                        sqlcmd = sqlcmd + " AND " + row[2] +  " LIKE '%" + obj[1] + "%'"
            
            respQ = getApi(sqlcmd)

            if (respQ["status"]=="ok"):
                
                rs = respQ["message"]
                if len(rs) == 0:
                    return "No existen registros de " + findText + ", se encuentra vacío. \n\n/menu - Muestra las opciones del menu principal."
               
                toSend = description + "\n\n"
                for idx in range(len(rs)):
                    for key in rs[idx]:
                        toSend += rs[idx][key] + " " 
                    
                    toSend += "\n"

                return toSend 
            
            else:
                print("ERROR", respQ)
                logger("ERROR", respQ, "CONTROLLER.LN.306")
                return "ERROR"
            
        elif row[0] == "F":
            return open_file(row[1])
    else:
        print(resp)
        logger("ERROR", resp, "CONTROLLER.LN.312")
        return "Los datos no se encuentran disponibles por el momento, e03."
    
    return textResult
    
