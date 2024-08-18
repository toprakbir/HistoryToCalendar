import os.path
import datetime
import sqlite3
from sqlite3 import OperationalError


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/calendar"]

path_to_db = 'History'
path_to_query = 'query.sql'
conn = sqlite3.connect(path_to_db)
cursor = conn.cursor()


#CHANGE THE VARIABLE DAYS TO SEARCH FROM 
comparison_date = datetime.datetime.now() - datetime.timedelta(days=7)
date_to = int(datetime.datetime.now().timestamp()) * 1000000


def filter_approximates(table):
    table.sort(key=lambda x: x[1])
    final_filtered_table = []
    for i in range(len(table)):
        start_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=int(table[i][1]) / 1000000 - 11644473600)
        if start_time > comparison_date:
            if i == 0:
                final_filtered_table.append(table[i])
            else:
                if table[i][2]:
                    if table[i][0] != table[i-1][0]:
                        final_filtered_table.append(table[i])
                    elif table[i][0] == table[i-1][0] and int(table[i][2]) > 1000000 * 60 * 60:
                        altered_row = (table[i][0], table[i][1], int(table[i][2]) + int(table[i-1][2]))
                        final_filtered_table.pop()
                        final_filtered_table.append(altered_row)
    return final_filtered_table


def execute_query_from_file(db_path, query_path):

    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
   # Read the query from the file
    with open(query_path, 'r') as file:
        query = file.read()

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Execute the query
        cursor.execute(query)
        table = cursor.fetchall()
        table = filter_approximates(table)
        return table

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        conn.close()
   

#ADDS AN EVENT TO THE GOOGLE CALENDAR FROM CHROME HISTORY
def add_event_from_history(service, table):
    table = get_large_tab(table)
    if not table:
       print("Could not add an event from history")
       return
    for row in table:
        seconds = int(row[1]) / 1000000 - 11644473600
        
        start_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=seconds) - datetime.timedelta(seconds = int(row[2]) / 1000000)
        end_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=seconds)
        summary = row[0]
        duration = row[2] / 1000000 / 3600 #DURATION
        description = str(summary) + " for " + str(duration) + " hours" 

        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'description': description,
        }
        print(str(event) + "\n")
        create_event = service.events().insert(calendarId='primary', body=event).execute()
        if not create_event:
           print("Could not add an event from history")    
    return

def add_event_from_terminal(service, table):
    summary = input("Enter the event summary: ")
    start_time = input("Enter the start time (YYYY-MM-DDTHH:MM:SS): ")
    end_time = input("Enter the end time (YYYY-MM-DDTHH:MM:SS): ")
    description = input("Enter the event description: ")

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'UTC',
        },
        'description': description,
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()

def update_event(service):
    events = get_event(service)
    if not events:
        print('No upcoming events found to be updated.')
        return
    event_id_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_id = event['id']
        event_id_list.append(event_id)
        print(f"Event ID: {event_id}, Start: {start}, Summary: {event['summary']}")

    choice = input("Which event would you like to update? (Enter the Event ID): ")
    while choice not in event_id_list:
        choice = input("Invalid Event ID. Please try again: ")

    event = service.events().get(calendarId='primary', eventId=choice).execute()

    selection = input("Which field would you like to update?\n1: Summary\n2: Start Time\n3: End Time\n")
    if selection == "1":
        new_summary = input(f"Enter new summary (current: {event['summary']}): ")
        event['summary'] = new_summary
    elif selection == "2":
        new_start = input(f"Enter new start time (YYYY-MM-DDTHH:MM:SS, current: {event['start'].get('dateTime', event['start'].get('date'))}): ")
        event['start']['dateTime'] = new_start
    elif selection == "3":
        new_end = input(f"Enter new end time (YYYY-MM-DDTHH:MM:SS, current: {event['end'].get('dateTime', event['end'].get('date'))}): ")
        event['end']['dateTime'] = new_end
        
    updated_event = service.events().update(calendarId='primary', eventId=choice, body=event).execute()
    
    print(f"Event succesfully updated: {updated_event['htmlLink']}")
    return

def delete_event(service):
    events = get_event(service)
    if not events:
        print('No upcoming events found to be deleted.')
        return
    
    event_id_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_id = event['id']
        event_id_list.append(event_id)
        print(f"Event ID: {event_id}, Start: {start}, Summary: {event['summary']}")

    choice = input("Which event would you like to delete? (Enter the Event ID): ")
    while choice not in event_id_list:
        choice = input("Invalid Event ID. Please try again: ")

    service.events().delete(calendarId='primary', eventId=choice).execute()
    
    print(f"Event with ID {choice} has been successfully deleted.")

def get_large_tab(table):
    large_tab = []
    threshold = 1000000 * 60 * 60
    for row in table:
        if row[2]:
            if int(row[2]) > threshold:
               large_tab.append(row)
    return large_tab

def get_event(service):
    now = datetime.datetime.now().isoformat() + 'Z'    
    events_list = service.events().list(calendarId='primary', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_list.get('items', [])
    return events

def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.now().isoformat() + 'Z'
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])


    sql_table = execute_query_from_file(path_to_db, path_to_query)
    add_event_from_history(service, sql_table)

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()


