from django.http import HttpResponse

from app.forms import EventForm


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
    events_result = service.events().list(settings.CALENDAR_ID, timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return HttpResponse('No upcoming events found.')
    else:
        return HttpResponse('<br>'.join([f"{event['start'].get('dateTime', event['start'].get('date'))}: {event['summary']}" for event in events]))
    

def create_event(request):
    credentials = service_account.Credentials.from_service_account_file(
        settings.SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=credentials)

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = {
                'summary': form.cleaned_data['summary'],
                'start': {
                    'dateTime': form.cleaned_data['start_time'].isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': form.cleaned_data['end_time'].isoformat(),
                    'timeZone': 'UTC',
                },
            }
            event = service.events().insert(calendarId=settings.CALENDAR_ID, body=event).execute()
            return HttpResponse(f'Event created: <a href="{event.get("htmlLink")}" target="_blank">View Event</a>')
    else:
        form = EventForm()

    return render(request, 'app/create_event.html', {'form': form})