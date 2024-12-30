# GoogleCalendar Automation 

This project aims to automate Google Calendar events with Calendar API and Chrome History database. It uses SQL queries to find necessary information about the history database such as the last visit time and the duration the tab was opened for. Eventually, with this information, it parses to the wanted values and creates an event for Google Calendar and then uses Google Calendar API service to put to the calendar of the registered email user's calendar.


# How it works

1) Copy the History file from Google Chrome to the project directory.
2) You currently need to add credentials.json, the reason this is not in the GitHub is because it includes sensitive information.
3) To run: enter python3 main.py.


# Current Issues with the Program
1) I need to configure a way that it is accessible to all users and not only users from my educational institution.
2) Figure out a way to dynamically locate history files in the computers' folder directory.
3) Make sure that the last modification is more accurate than the older version.
4) Since Chrome does not track if the tab was inactive during the duration period, the system cannot be 100% accurate on how long you have spent on that specific tab.
  4.a) I have no way of fixing this and it is suggested to close the tab as soon as you are done with the tab to avoid hours and days long duration periods
5) Issue with requirements.txt: will be issued a fix right after the Christmas break as the main project lies within my old computer.

