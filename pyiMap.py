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
params['ManageUser']:str   = ""
params['ManagePass']:str   = ""

# ################################
# parse_Mailbox
# 
# Durchsucht die Mailbox
#
# Parameter: MB - Das Mailbox-Handle
def parse_Mailbox(MB):
   if params['DEBUGLEVEL'] >= 5:
      logging.debug("*** parse_Mailbox *** start ***")
   
   Status, Messages = MB.select("inbox")
   
   if Status != "OK":
      logging.critical("Select to INBOX delivers NOT OK - Terminating")
      exit(-1)
   
   logging.info("Got: "+str(Messages)+ "Messages")
   
   logging.info("Starting Message Search")
   result, Message = MB.search(None,'ALL')
   
   # In Message ist jetzt ein String mit allen Nummern die zutreffend sind durch Space getrennt

   
   if params['DEBUGLEVEL'] >= 5:
      logging.debug("RESULT:" +result)
      logging.debug("Messages: "+str(Message[0]))
      
   # Daraus machen wir jetzt eine Liste von "Nummern"   
   MessageNumbers = list(map(int, Message[0].split()))
   
   print(MessageNumbers)
   for I in MessageNumbers:
      # Aus dem Interger ein Byte machen....och wie war Py2 einfach
      erg = str(I).encode()
      
   exit()   
   
   
   
   for I in MessageNumbers:
      result, msgBody = MB.fetch(I,'(RFC822)')
      print("result: "+result)
      print("msg: "+msgBody)

   
   
   # wir arbeiten nun durch die Mailbox
   for I in range(int(Messages[0])):
      # Jetzt "zerpfluecken wir die emails"
      print(I)
      result, msgBody = MB.fetch(bytes(I), '(RFC822)')
      print("result: "+result)
      print("msg: "+msgBody)
   
   if params['DEBUGLEVEL'] >= 5:
      logging.debug("--- parse_Mailbox --- end ---")   
   


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
      params['DEBUGLEVEL'] = int(pyiMapConfig['Default']['Debuglevel'])
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
   logging.info("Loglevel: "+str(params['DEBUGLEVEL']))
   
   try:
      params['IMAPServer'] = pyiMapConfig['imap']['server']
   except:
      print("imap -> server nicht gesetzt")
      exit(-1)

   try:
      params['IMAPPort'] = int(pyiMapConfig['imap']['port'])
   except:
      print("imap -> port nicht gesetzt")
      exit(-1)
    
   # Argumente Parsen
   parser = argparse.ArgumentParser()
   parser.add_argument("user",help="Username fuer imap")
   parser.add_argument("password",help="Password fuer imap-User")
   args = parser.parse_args()
   
   print("Das ist gefaelligst nur temporaer!!")
   print(args.password)
   print(args.user)

   if params['DEBUGLEVEL'] >= 5:
      logging.debug("Establish IMAP Connection to Server")
   
   # Verbindung zum IMAP aufbauen
   MailServer = imaplib.IMAP4(host=params['IMAPServer'],port=params['IMAPPort'])
   
   # Login in IMAP
   MailServer.login(args.user, args.password)
   
   # Mailbox parsen :-)
   parse_Mailbox(MailServer) 
   
   if params['DEBUGLEVEL'] >= 5:
      logging.debug("Closing IMAP Connection to Mailbox")
   MailServer.close()
   
   if params['DEBUGLEVEL'] >= 5:
      logging.debug("Logout from IMAP-Server")   
   MailServer.logout()
   
   logging.info("Programm ended")