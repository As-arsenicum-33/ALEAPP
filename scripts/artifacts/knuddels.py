__artifacts_v2__ = {
    "get_knuddels_chats": {
        "name": "Knuddels - Chats",
        "description": "Extracts Knuddels Chats from database files",
        "author": "@As-arsenicum-33",
        "version": "0.0.1",
        "date": "2025-05-03",
        "requirements": "none",
        "category": "Knuddels",
        "notes": "",
        "paths": ('*/com.knuddels.android/databases/knuddels*',),
        "function": "get_knuddels_chats"
    },
}

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_knuddels_chats(files_found, report_folder, seeker, wrap_text):
    
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)

        if(file_found.endswith("-journal")):
            pass 
        else:
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            nickname, message, 
            datetime(thread.timestamp/1000, 'unixepoch','localtime') AS "timestamp", cid AS "chat_id",
            thread.sender AS "thread_table_user_id",
            users.id AS "users_table_user_id"
            FROM thread, users
            WHERE users.id = thread.sender 
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)

            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], "chat_" + str(row[3]) + "_", file_found, row[4], row[5]))

            if len(data_list) > 0:
                report = ArtifactHtmlReport('Knuddels Messages')
                report.start_artifact_report(report_folder, f'Knuddels Messages')
                report.add_script()
                data_headers = ('nickname', 'message', 'timestamp', 'chat_id', 'source database', 'thread_table_user_id', 'users_table_user_id')
                report.write_artifact_data_table(data_headers, data_list, 'See report')
                report.end_artifact_report()
                
                tsvname = f'Knuddels'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = f'Knuddels'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc(f'No Knuddels Chats available')


