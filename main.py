import os.path
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/calendar"]

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
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])

    while True:
        action = input("What would you like to do?\n1: Add Event\n2: Update Event\n3: Delete Event\n4: Exit\n")
        if action == "1":
            add_event(service)
        elif action == "2":
            update_event(service)
        elif action == "3":
            delete_event(service)
        elif action == "4":
            break
        else:
            print("Invalid input. Please try again.")
            
  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()


