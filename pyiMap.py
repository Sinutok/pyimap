#
# Diverses IMAP-Zeugs in Python
# 
# Der erste Versuch
# Das Ganze wird in 3.6+ geschrieben, aber wird sehr 2.xig aussehen, weil dies das erste 3er Projekt ist.
# Code-Stil-Aenderungen sind wahrscheinlich, schluderei auch.
#
# 2017-03-29 - Philospohieren
#

params = {}    # Mein Repository - Unelegant aber praktisch


# IMPORTS
from time import localtime,strftime
from sys import argv, exit
import configparser              # Damit mit einer INI gearbeitet werden kann
import logging                   # LOG-Mechanismus
import argparse                  # Argumente zur Uebergabe
import imaplib                   # imap-Zeugs


params['DEBUGLEVEL']:int   = 0
params['LogFile']:str      = ""
params['IMAPServer']:str   = ""
params['IMAPPort']:int     = 0

# ################################
# connect2imap
# 
# Stellt die Verbindung zum IMAP-Server her
#
def connect2imap():
   print("EMPTY")
   


# ################################
# 
# MAIN
#
if __name__ == '__main__':
   """ Wir sind nicht inportierbar, as ususal """
   
   pyiMapConfig = configparser.ConfigParser()   # Configparser initialisieren
   
   pyiMapConfig.read("./pyiMap.ini")            # Ini-File einlesen
   
   # Checken ob es ein Defaul gibt
   if 'Default' not in pyiMapConfig:
      print("[Default]-Sektion in ini fehlt, oder INI-File unlesbar!")
      exit(-1)
      
   # DEBUGLEVEL finden
   try:
      params['DEBUGLEVEL'] = pyiMapConfig['Default']['Debuglevel']
   except:
      print("Default -> Loglevel nicht erkennbar")
      exit(-1)
   
   # Logfilename
   try:
      params['LogFile'] = pyiMapConfig['Default']['LogFile']
   except:
      print("Default -> Logfile nicht gesetzt")
      exit(-1)
   
   logging.basicConfig(filename=".\\"+params['LogFile'], level=logging.DEBUG, format='%(asctime)s - %(message)s')
   
   logging.info("Programm startet")
   logging.info("Loglevel: "+params['DEBUGLEVEL'])
   
   try:
      params['IMAPServer'] = pyiMapConfig['imap']['server']
   except:
      print("imap -> server nicht gesetzt")
      exit(-1)

   try:
      params['IMAPPort'] = pyiMapConfig['imap']['port']
   except:
      print("imap -> port nicht gesetzt")
      exit(-1)
    
   parser = argparse.ArgumentParser()
   parser.add_argument("user",help="Username fuer imap")
   parser.add_argument("password",help="Password fuer imap-User")
   args = parser.parse_args()
   
   print(args.password)
   print(args.user)
   #connect2IMAP()
      
   logging.info("Programm ended")