import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone

# Path to your credentials JSON file
credentials_path = 'path/to/credentials.json'

# Load credentials from JSON file
credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=['https://www.googleapis.com/auth/calendar'])

# Build the Google Calendar service
service = build('calendar', 'v3', credentials=credentials)

SCOPES = ['https://www.googleapis.com/auth/calendar']

def add_event(service):
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

    print(f"Event created: {created_event['htmlLink']}")

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

def get_event(service):
    present = datetime.now(timezone.utc).isoformat()
    events_list = service.events().list(calendarId='primary', timeMin=present, maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_list.get('items', [])
    return events

def main():
    # Start the OAuth flow to get new credentials
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Build the Google Calendar service
    service = build('calendar', 'v3', credentials=creds)
    
    # Call the Calendar API
    now = datetime.now(timezone.utc).isoformat()
    
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

    while(choice == None):
        choice = input("1: Update\n2: Add\n3: Delete\n")
        if choice == "1":
            update_event(service)
        elif choice == "2":
            add_event(service)
        elif choice == "3":
            delete_event(service)
        else:
            choice = None
if __name__ == '__main__':
    main()

