# -*- coding: utf-8 -*-
"""
Convert your WhatsApp messages to Signal (media not included) using Python terminal
Android only!

Autor: Gilles Van Gestel
https://www.linkedin.com/in/gillesvangestel
please contact me for information, collaboration or suggestions involving the code

Steps:
    1. Export all required conversations from WhatsApp to desktop
        * Open conversation in WhatsApp
        * Three dots
        * More...
        * Export conversation !without media!
        * Send to desktop using mail, Dropbox, Google Drive, ...
    2. Save the exported files together in one directory and reference that 
       directory below
        * for example: directory = "C://Users/Gilles/Files/"
"""
directory = "C://Users/Gilles/Files/"

"""
    3. Change the names of all files to a combination of:
        * Contact phone number
        * Contact name
        * for example: "+32123456789-Gilles Van Gestel" 
                        or "5555551234-Gilles Van Gestel" 
                        or ...
        * It is crucial that the contact name is the same name as your contact 
          on WhatsApp (so not only the first name), you can check the name 
          in the text file to be sure.
    4. Run the code
    5. Find the resulting file "sms-00000000000000.xml" in your directory
    6. Send "sms-00000000000000.xml" to your phone using mail, Dropbox, Google Drive, ...
    7. Backup your system SMS messages (not WhatsApp!) using SMSBackupAndRestore
        * https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore
    8. Erase all system SMS messages
    9. Use SMSBackupAndRestore to restore "sms-00000000000000.xml" into the system SMS database
    10. Use Signal to import your system SMS database
        * Three dots
        * Settings
        * Sms and mms
        * Sms turned on
        * Locate "sms-00000000000000.xml" in your phone storage
    11. Turn signal SMS management back off if you do not want to use it
    12. Erase all system SMS messages again
    13. Restore your original SMS messages that you backed up in (7.)
    14. You should now have your WhatsApp messages in Signal
"""

# you can uncomment the following lines if your phone is in Dutch
# import locale
# locale.setlocale(locale.LC_ALL, 'nl_NL')

import os
from xml.dom import minidom
from datetime import datetime

def is_date(string, fuzzy=False):
    try: 
        # depending on what date-format your WhatsApp uses, you might need to change this
        datetime.strptime(string, '%d/%m/%Y')
        return True

    except ValueError:
        return False  

root = minidom.Document()
smses = root.createElement("smses")
root.appendChild(smses)

count = 0
text = 0
sms = 0

for file in os.listdir(directory):
    if file.endswith(".txt"):
        
        full_file = directory + "/" + file
        filename = os.path.splitext(file)[0]
        file_parts = filename.split("-")
        
        phone_number = file_parts[0]
        contact = file_parts[1]

        messages_to_parse = open(full_file, encoding="utf8")
        for message_line in messages_to_parse:
            
            if not is_date(message_line.split(" ", 1)[0]):
                if text == 0 or sms == 0:
                    continue
                text = text + "\n" + message_line.rstrip().lstrip()
                sms.setAttribute("body", text)
                continue
            
            metadata_and_text = message_line.rstrip().split(":", 2)
            metadata = ":".join(metadata_and_text[:2])
            if len(metadata_and_text) !=3:
                print("wrong composition of metadata and text: message skipped")
                print(message_line)
                continue
            text = metadata_and_text[2].lstrip()
            
            metadata_parts = metadata.split(" ", 3)
            if len(metadata_parts) != 4:
                print("wrong composition of metadata parts: message skipped")
                print(message_line)
                continue
            
            date_in_wrong_format = metadata_parts[0]
            time_in_wrong_format = metadata_parts[1]
            sender = metadata_parts[3]

            # 1 = you receive, 2 = you send
            receive_or_send = "1"
            if contact != sender:
                receive_or_send = "2"
            
            date_parts = date_in_wrong_format.split("/")
            time_parts = time_in_wrong_format.split(":")
            
            date_object = datetime(int(date_parts[2]), int(date_parts[1]), int(date_parts[0]), int(time_parts[0]), int(time_parts[1]), 00)
            timestamp = datetime.timestamp(date_object)
            
            # depending on what date-format your WhatsApp uses, you might need to change this
            date = date_object.strftime("%d %b. %Y %H:%M:%S")
                        
            sms = root.createElement("sms")
            sms.setAttribute("protocol", "0")
            sms.setAttribute("address", phone_number)
            sms.setAttribute("date", str(int(timestamp))+"000")
            sms.setAttribute("type", receive_or_send)
            sms.setAttribute("subject", "null")
            sms.setAttribute("body", text)
            sms.setAttribute("toa", "null")
            sms.setAttribute("sc_toa", "null")
            sms.setAttribute("service_center", "null")
            sms.setAttribute("read", "1")
            sms.setAttribute("status", "-1")
            sms.setAttribute("locked", "0")
            sms.setAttribute("date_sent", "0")
            sms.setAttribute("sub_id","-1")
            sms.setAttribute("readable_date", date)
            sms.setAttribute("contact_name", contact)
            smses.appendChild(sms)
            count += 1

smses.setAttribute("count", str(count))
smses.setAttribute("backup_set", "fe37c586-4242-520a-b72d-39488dbe1930")
smses.setAttribute("backup_date", str(int(datetime.timestamp(datetime.now())*1000)))
smses.setAttribute("type", "full")

xml_str = root.toprettyxml()
with open(directory + "/" + "sms-00000000000000.xml", "w", encoding="utf-8") as f:
    f.write(xml_str)