#
# Diverses IMAP-Zeugs in Python
# 
# Der erste Versuch
# Das Ganze wird in 3.6+ geschrieben, aber wird sehr 2.xig aussehen, weil dies das erste 3er Projekt ist.
# Code-Stil-Aenderungen sind wahrscheinlich, schluderei auch.
#
# 2017-03-29 - Philospohieren
# 2017-07-22 - Python 3 kotzt mich an.... somit setze ich es in Py2 um
#

params = {}    # Mein Repository - Unelegant aber praktisch


# IMPORTS
from time import localtime,strftime
from PyToolsMG import mg_tool,mg_config
from sys import argv, exit
import ConfigParser              # Damit mit einer INI gearbeitet werden kann
import logging                   # LOG-Mechanismus
import argparse                  # Argumente zur Uebergabe
import imaplib                   # imap-Zeugs
import email                     # Email-Handling
import email.header              # Email-Header-Zeugs

import pprint

params['DEBUGLEVEL'] = 0
params['Delimiter'] = ""
params['folder'] = []
params['LogFile'] = ""
params['IMAPServer'] = ""
params['IMAPPort'] = 0
params['ManageUser'] = ""
params['ManagePass'] = ""
params['Mail2FolderMapping']   = {} # EmailAddresse:['Ordner']

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
# MoveMessage
#
# Verschiebt die Message in den richtigen Ordner
#
# Parameter: Empfaenger - An wen die Message ging
def MoveMessage(MB,zu_wem, nachrichtennummer):
   if params['DEBUGLEVEL'] >= 5:
      logging.debug("*** MoveMessage *** start ***")
      logging.debug("zu_wem: " + str(zu_wem))
      
   zielordner = params['Mail2FolderMapping'][zu_wem]
   
   alleordnervorhanden = True
   # ALLE Ordner holen
   result,alleordner = MB.list()
   if result != "OK":
      logging.critical("MB.LIST fehlgeschlagen, EXIT")
      exit(-1)
   # Result von MB.list war oke, ergo weiter
   for I in zielordner:
      if params['DEBUGLEVEL'] >= 5:
         logging.debug("Nachrichtennumer: "+str(nachrichtennummer))
         logging.debug("Zielordner: "+ str(I))
      # Checken ob Ordner vorhanden
      ordnerfound = False
      for J in alleordner:
         print "J: " + str(J)
         if str(I) in str(J):
            ordnerfound = True
         if ordnerfound == True:
            break
      
      if ordnerfound == False:
         logging.info("Ordner: " + str(I) + " nicht gefunden, wird erstellt")
         result, data = MB.create(str(I))
         alleordnervorhanden = False
         print data
         if result == 'OK':
            logging.info("IMAP-Folder created: "+ str(I) +" " + str(b' '.join(data)))
         else:
            logging.error("Erstellung IMAP-Folder: "+str(I)+" fehlgeschlagen!! EXIT!!")
            logging.error("Nachrichtennummer: "+str(nachrichtennummer).encode())
            exit(-1)
   
   if alleordnervorhanden == False:
      # Es wurde ein neuer Ordner erstellt, also nochmals einlesen
      result,alleordner = MB.list()
      if result != "OK":
         logging.critical("2. MB.LIST fehlgeschlagen, EXIT")
         exit(-1)
      # Result von MB.list war oke, ergo weiter

   # Wenn er bis jetzt nicht ausgestiegen ist, dann  ist wohl alles oke
   # also kopieren
   for I in zielordner:
      result, data = MB.uid('copy',nachrichtennummer,'"'+str(I)+'"')    
      if result == 'NO':
         print "Copy war nix: "+str(b' '.join(data))
         exit(-1)
         # Copy hat nicht geklappt
      if params['DEBUGLEVEL'] >= 5:
         logging.debug("MB.copy() Result: "+str(result))
         
      ### Sie wurde kopiert also zum loeschen vorbereiten
      result, data = MB.uid('store', nachrichtennummer,'+FLAGS',('\\Deleted'))
      #result, data = MB.store(nachrichtennummer,'+FLAGS','\\Deleted')
      if result != 'OK':
         print("Store-Deleted war nix")
         print(result)
         print(data)
         exit(-1)
      else:
         logging.info("Delete-Flag on: "+str(nachrichtennummer))
      if params['DEBUGLEVEL'] >= 5:
         print("STORe")
         print(data)
         print(result)
         logging.debug("MB.store - Flags Deleted: "+str(result))
      
      ### ERSTMAL HIERNACH ALLES WEG, DELETED WIRD NICHT GESETZT
      # Jetzt wird sie geloescht
      result, data = MB.expunge()
      if result != 'OK':
         print("Expunge ging nicht!")
         print(result)
         print(data)
         exit(-1)
      else:
         print("Expunge")
         print(data)
         logging.info("Expunge erfolgreich fuer: "+str(nachrichtennummer))
         
   if params['DEBUGLEVEL'] >= 5:
      logging.debug("=== MoveMessage === END ===")
   
# ################################
# parse_Mailbox
# 
# Durchsucht die Mailbox
#
# Parameter: MB - Das Mailbox-Handle
def parse_Mailbox(MB):
   if params['DEBUGLEVEL'] >= 5:
      logging.debug("*** parse_Mailbox *** start ***")
   
   #Status, Messages = MB.select("INBOX")
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
   
   MessageNumbers = Message[0].split()
   
   # Message holen
   for I in MessageNumbers:
      #erg = str(I).encode() # Int to Byte
      result, data = MB.uid('fetch', I, '(BODY.PEEK[HEADER])')
      #MB.uid('fetch', I, '(RFC822)')
      
      if data == None:
         print "DATA NONE! MessageNumber: "+str(I)
         logging.critical("No Data at fetch! MessageNumber: "+ str(I))
         exit(-1)
      
      if params['DEBUGLEVEL'] >= 5:
         logging.debug("Messagenummer: "+ str(I))
         logging.debug("Result: "+result)
         pprint.pprint(data)
         #logging.debug("headerPart: " + str(b','.join(headerPart)))
      
      if result == "OK":
         Empfaenger = AnalyseMail(data[0])
         if params['DEBUGLEVEL'] >= 5:
            logging.debug("Empfaenger: " + Empfaenger)
         pprint.pprint(Empfaenger)
         #email_message = email.message_from_bytes(data[0][1])
         #hdr = email.header.make_header(email.header.decode_header(email_message['To']))
         #print("HDR: "+ str(hdr))
      else:
         logger.error("* ERROR MB Fetch des Headers brachte Error: "+ str(result))
         logger.error("** MessageID: "+ str(I))
         exit()       
      
      # Jetzt muss sie verschoben werden, das kann nach dem Result, weil das ist ja ok, sonst
      # waere es vorher ausgestiegen.
      
      MoveMessage(MB,Empfaenger, I)
      
   if params['DEBUGLEVEL'] >= 5:
      logging.debug("--- parse_Mailbox --- end ---")   
   


# ################################
# 
# MAIN
#
if __name__ == '__main__':
   """ Wir sind nicht inportierbar, as ususal """
   
   # Configuration
   configuration = mg_config("pyiMap.ini")
   
   # DEBUG aus config setzen
   params['DEBUGLEVEL'] = int(configuration.get_values("Default", "Debuglevel"))
   if not isinstance(params['DEBUGLEVEL'],int):
      print "Debug-Wert kein Integer"
      exit(-1)    
   
   # Log-File aus config setzen
   params['LogFile'] = configuration.get_values("Default", "LogFile")
   #params['logfile'] = LOG+'-'+strftime("%y%m%d-%H%M%S",params['startzeit'])+".log"
   
   logging.basicConfig(filename=".\\"+params['LogFile'], level=logging.DEBUG, format='%(asctime)s - %(message)s')
   
   logging.info("*=*=*=*=*=*=*=* Programm startet *=*=*=*=*=*=*=*=*")
   logging.info("Loglevel: "+str(params['DEBUGLEVEL']))
   
   #IMAP DELIMITER
   params['Delimiter'] = str(configuration.get_values("Default","Delimiter"))
   if not isinstance(params['Delimiter'],str):
      print "Delimiter ist nicht gesetzt"
      exit(-1)
      
   # IMAP - Server
   params['IMAPServer'] = configuration.get_values("imap","server")
   
   # IMAP - Port
   params['IMAPPort'] = int(configuration.get_values("imap","port"))
   
   # Jetzt starten wird das Mail2FolderMapping
   # Sicher man koennte mehr Logik in die App legen,
   # aber es soll ja erstmal irdgendwann fertig werden
   
   for I in xrange(1,int(configuration.get_values("folders", "amount"))+1):
      params['folder'].append(configuration.get_values("folders", str(I)))
      
   for I in params['folder']:
      for J in configuration.get_items(I):
         if J in params['Mail2FolderMapping']:
            params['Mail2FolderMapping'][J].append(configuration.get_values(I,J))
         else:
            params['Mail2FolderMapping'][J] = [configuration.get_values(I,J)]

   # Argumente Parsen
   parser = argparse.ArgumentParser()
   parser.add_argument("user",help="Username fuer imap")
   parser.add_argument("password",help="Password fuer imap-User")
   args = parser.parse_args()
   
   print "Das ist gefaelligst nur temporaer!!"
   print args.password
   print args.user

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