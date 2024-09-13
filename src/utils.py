from datetime import datetime
from pprint import pprint
# import logging
import json

# def setLogging(msg):
#     logging.basicConfig(filename='chat.log', level=logging.DEBUG)
#     logging.debug(msg)

def logger(type, msg, line):
    ddate = datetime.now()
    fecha = ddate.strftime("%Y-%m-%d %H:%M:%S")
    logtext = f"{fecha} {type} {line} {msg}\n"
    file = open("chat.log","a")
    file.write(logtext)
    file.close()
    
    
    
def open_file(file=''):
    file = open(file)
    content = file.readlines()
    rec=0
    tex = ""
    for c in content:
       tex = tex + c 
    file.close()
    return tex