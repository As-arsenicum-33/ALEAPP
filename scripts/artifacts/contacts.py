import os
import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, does_column_exist_in_db

def get_contacts(files_found, report_folder, seeker, wrap_text):

    source_file = ''
    data_list = []
    
    for file_found in files_found:
        
        file_name = str(file_found)
        if not os.path.basename(file_name) == 'contacts2.db' and \
           not os.path.basename(file_name) == 'contacts.db': # skip -journal and other files
            continue

        source_file = file_found.replace(seeker.data_folder, '')

        db = open_sqlite_db_readonly(file_name)
        cursor = db.cursor()
        try:
            if does_column_exist_in_db(file_name, 'contacts', 'name_raw_contact_id'):
                cursor.execute('''
                    SELECT mimetype, data1, name_raw_contact.display_name AS display_name
                      FROM raw_contacts JOIN contacts ON (raw_contacts.contact_id=contacts._id)
                      JOIN raw_contacts AS name_raw_contact ON(name_raw_contact_id=name_raw_contact._id) 
                      LEFT OUTER JOIN data ON (data.raw_contact_id=raw_contacts._id) 
                      LEFT OUTER JOIN mimetypes ON (data.mimetype_id=mimetypes._id) 
                     WHERE mimetype = 'vnd.android.cursor.item/phone_v2' OR mimetype = 'vnd.android.cursor.item/email_v2'
                     ORDER BY name_raw_contact.display_name ASC;''')
            else:
                cursor.execute('''
                    SELECT mimetype, data1, raw_contacts.display_name AS display_name
                      FROM raw_contacts JOIN contacts ON (raw_contacts.contact_id=contacts._id)
                      LEFT OUTER JOIN data ON (data.raw_contact_id=raw_contacts._id)
                      LEFT OUTER JOIN mimetypes ON (data.mimetype_id=mimetypes._id)
                      WHERE mimetype = 'vnd.android.cursor.item/phone_v2' OR mimetype = 'vnd.android.cursor.item/email_v2'
                     ORDER BY raw_contacts.display_name ASC;''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    phoneNumber = None
                    emailAddr = None
                    if row[0] == "vnd.android.cursor.item/phone_v2":
                        phoneNumber = row[1]                                      
                    else:
                        emailAddr = row[1]

                    data_list.append((row[0], row[1], row[2], phoneNumber, emailAddr, file_name))
            
        except Exception as e:
            print (e)
            usageentries = 0
            
        db.close()
    
    if data_list:
        report = ArtifactHtmlReport('Contacts')
        report.start_artifact_report(report_folder, 'Contacts')
        report.add_script()
        data_headers = ('Mimetype','Data 1', 'Display Name', 'Phone Number', 'Email Address', 'Source File') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Contacts'
        tsv(report_folder, data_headers, data_list, tsvname, source_file)
        
    else:
        logfunc('No Contacts found')

# 'contacts':('Contacts', ('**/com.android.providers.contacts/databases/contact*', '**/com.sec.android.provider.logsprovider/databases/logs.db*')),
__artifacts__ = {
    "Contacts": (
        "Contacts",
        ('*/com.android.providers.contacts/databases/contact*', '*/com.sec.android.provider.logsprovider/databases/logs.db*', '*/com.samsung.android.providers.contacts/databases/contact*'),
        get_contacts)
}
