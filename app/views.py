from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import EventForm
from .utils import get_google_calendar_service
import datetime

def index(request):
    return render(request, 'app/index.html')

def google_calendar_events(request):
    service = get_google_calendar_service()

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=settings.CALENDAR_ID, timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    events_list = []
    for event in events:
        event_start_str = event['start'].get('dateTime', event['start'].get('date'))
        event_start = datetime.datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
        event_summary = event['summary']
        event_link = event['htmlLink']
        events_list.append({'start': event_start, 'summary': event_summary, 'link': event_link})

    context = {
        'events': events_list
    }
    return render(request, 'app/events.html', context)

def create_event(request):
    service = get_google_calendar_service()

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
            return redirect('events')

    else:
        form = EventForm()

    return render(request, 'app/create_event.html', {'form': form})