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
import email                     # Email-Handling

import pprint

params['DEBUGLEVEL']:int   = 0
params['Delimiter']:str    = ""
params['LogFile']:str      = ""
params['IMAPServer']:str   = ""
params['IMAPPort']:int     = 0
params['ManageUser']:str   = ""
params['ManagePass']:str   = ""
params['Mail2FolderMapping']   = {}

# ################################
# AnalyseMail
#
# Liefert den TO zurueck
#
# Parameter:
# der_Header - Subject, From,To in Tuple
#
# Return:
# To
def AnalyseMail(der_Header):
   if params['DEBUGLEVEL'] >= 5:
      logging.debug("*** AnalyseMail *** start ***")
   pprint.pprint(der_Header[1])
   email_message = email.message_from_string(der_Header[1].decode("utf-8"))
   logging.info("Found Mail-To: " + email_message['To'])
      
   if params['DEBUGLEVEL'] >= 5:
      logging.debug("=== AnalyseMail === END ===")
   
   return email_message['To']

# ################################
# DetermineMailFolder
#
# Macht aus dem TO: die Ordner-Notation
#
# Parameter: zu_wem - Der TO
def DetermineMailFolder(zu_wem):
   if params['DEBUGLEVEL'] >= 5:
      logging.debug("*** DetermineMailFolder *** start ***")

   # Die Mailfolder sind mit _ gemacht
   tmp_list = zu_wem.split('@')
   
   if params['DEBUGLEVEL'] >= 5:
      logging.debug("=== DetermineMailFolder === END ===")
   
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
   #Message-ID als Basis nicht die Nummer, die ID bleibt gleich
   result, Message = MB.uid('search',None, "ALL")
   
   # In Message ist jetzt ein String mit allen Nummern die zutreffend sind durch Space getrennt

   if params['DEBUGLEVEL'] >= 5:
      logging.debug("RESULT:" +result)
      logging.debug("Messages: "+str(Message[0]))
      
   # Daraus machen wir jetzt eine Liste von "Nummern"   
   MessageNumbers = list(map(int, Message[0].split()))
   
   print(MessageNumbers)
   
   # Hier der Test nur den To, Subject + From zu pollen, warum auch die ganze Nachricht
   
   for I in MessageNumbers:
      erg = str(I).encode() # Int to Byte
      result, headerPart = MB.fetch(erg,'(BODY[HEADER.FIELDS (SUBJECT FROM TO)])')
      if result == "OK":
         Empfaenger = AnalyseMail(headerPart[0])
      else:
         logger.error("* ERROR MB Fetch des Headers brachte Error: "+ str(result))
         logger.error("** MessageID: "+ str(I))
         exit()       
      
      # Wir haben jetzt zu wem es geht, damit kann man den Ordner finden bzw. bauen.
      DetermineMailFolder(Empfaenger)
      
   exit()
   
   for I in MessageNumbers:
      # Aus dem Interger ein Byte machen....och wie war Py2 einfach
      erg = str(I).encode()
      result, msgBody = MB.fetch(erg,'(RFC822)')
      if result == "OK":
         AnalyseMail(msgBody[0])      
   
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
   
   # Checken ob es ein Default gibt
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
   
   #IMAP DELIMITER
   try:
      params['delimiter'] = pyiMapConfig['Default']['delimiter']
   except:
      print("Default -> Delimiter nicht gesetzt")
      exit(-1)
      
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
   
   # Jetzt starten wird das Mail2FolderMapping
   # Sicher man koennte mehr Logik in die App legen,
   # aber es soll ja erstmal irdgendwann fertig werden
   
   for I in range(1,len(pyiMapConfig['folders'])+1):
      tmp_sectName = pyiMapConfig['folders'][str(I)]
      
      for J in pyiMapConfig[tmp_sectName]:
         if tmp_sectName not in params['Mail2FolderMapping']:
            params['Mail2FolderMapping'][J] = [pyiMapConfig[tmp_sectName][str(J)]]
         else:
            params['Mail2FolderMapping'][J].append(pyiMapConfig[tmp_sectName][str(J)])
                                          
                                              
      #try:
         #params['Mail2FolderMapping'][pyiMapConfig['folders'][str(I)]] = 
      #except:
         #print("FolderWildCard: "+str(I)+ " nicht lesbar")
         #exit(-1)
      
   #print(len(pyiMapConfig['folderwildcard']))
   pprint.pprint(params)
   exit()
      
   pprint.pprint(params)
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