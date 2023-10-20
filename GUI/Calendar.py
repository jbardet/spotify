import os
import datetime
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class Calendar():
    """
    Handle the calendar if we want to print it in the GUI
    """
    def __init__(self) -> None:
        """
        Initialize the calendar class with credentials and the calendar id
        """
        # If modifying these scopes, delete the file token.json.
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        self.creds = self.get_token()
        self.calendar_id = ""
        # id_client = ""
        # client_secret = ""
        # token_url = "https://accounts.google.com/o/oauth2/v2/auth"
        # url = "https://www.googleapis.com/calendar/v3"
        # redirect_uri = "http://localhost:8080"
        # api_call = "https://www.googleapis.com/calendar/v3/users/me/calendarList"
        # link_to_today = "https://calendar.google.com/calendar/u/0/r/day"

    def get_token(self) -> Credentials:
        """
        Get the credentials token to access the google calendar API

        :return: the credentials needed to access the google calendar API
        :rtype: Credentials
        """
        creds = None

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('creditentials/token.json'):
            creds = Credentials.from_authorized_user_file('creditentials/token.json',
                                                          self.scopes)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'creditentials/credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('creditentials/token.json', 'w') as token:
                token.write(creds.to_json())

        return creds

    def get_today_events(self) -> None:
        """
        Get today's event from the calendar
        """

        # see https://developers.google.com/calendar/api/quickstart/python
        try:
            service = build('calendar', 'v3', credentials=self.creds)

            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            print('Getting the upcoming 10 events')
            events_result = service.events().list(calendarId=self.calendar_id,
                                                  timeMin=now, maxResults=10,
                                                  singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')
                return

            today_events = []

            # Prints the start and name of the next 10 events
            for event in events:
                start = event['start'].get('dateTime',
                                           event['start'].get('date'))
                start_time = datetime.datetime.strptime(start,
                                                        "%Y-%m-%dT%H:%M:%S%z")
                # if the event is today keep it
                if start_time.date() == datetime.datetime.today().date():
                    end = event['start'].get('dateTime',
                                             event['start'].get('date'))
                    print(start)
                    try:
                        title = event['summary']
                    except KeyError:
                        title = "No title"
                    try:
                        description = event['description']
                    except KeyError:
                        description = "No description"
                    today_events.append([title, description, start, end])

        except HttpError as error:
            print('An error occurred: %s' % error)

        print(today_events)
