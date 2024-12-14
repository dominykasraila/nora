from django.http import HttpResponse


def index(request):
    return HttpResponse("Labas, pasauli!")

from django.shortcuts import render
from django.http import HttpResponse
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
import os
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/calendar']

def google_calendar_events(request):
    credentials = service_account.Credentials.from_service_account_file(
        settings.SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=credentials)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='e1aef64be663dfd8714df4818496270fa042c528d0664cf42e9b142144fefe2f@group.calendar.google.com', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return HttpResponse('No upcoming events found.')
    else:
        return HttpResponse('<br>'.join([f"{event['start'].get('dateTime', event['start'].get('date'))}: {event['summary']}" for event in events]))