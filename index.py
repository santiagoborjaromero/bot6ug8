import sys
import time
import telepot
from telepot.loop import MessageLoop
from pprint import pprint
from concurrent.futures import thread
import threading
import os

import config.init

os.system('cls')

from config.init import TELEGRAM_TOKEN
from src.bridgecontroller import processing
from src.utils import logger

bot = telepot.Bot(TELEGRAM_TOKEN)

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    
    thread = threading.Thread(target=processing, args=(content_type,msg, chat_type, chat_id, bot, ))
    thread.start()
   

if __name__ == "__main__":
    print ('Soy 6GU8BOT v0.2, comencemos')
    
    MessageLoop(bot, handle).run_as_thread()
    print ('Escuchando ...')

    while 1:
        time.sleep(10)
        
        
        