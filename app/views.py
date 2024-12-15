from urllib.parse import urlencode
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ReservationForm
from .utils import get_google_calendar_service
import datetime
from collections import defaultdict

def index(request):
    return render(request, 'app/index.html')

def available_slots(request):
    service = get_google_calendar_service()

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    events_result = service.events().list(
        calendarId=settings.CALENDAR_ID,
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime',
        q='Langas',
    ).execute()

    reservations_result = service.events().list(
        calendarId=settings.CALENDAR_ID,
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime',
        q='Rezervacija',
    ).execute()

    events = events_result.get('items', [])
    reservations = reservations_result.get('items', [])

    slots_by_date = defaultdict(list)
    for event in events:
        event_start_str = event['start'].get('dateTime', event['start'].get('date'))
        event_start = datetime.datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
        event_end_str = event['end'].get('dateTime', event['end'].get('date'))
        event_end = datetime.datetime.fromisoformat(event_end_str.replace('Z', '+00:00'))
        
        slot_start = event_start
        while slot_start + datetime.timedelta(minutes=60) <= event_end:
            slot_end = slot_start + datetime.timedelta(minutes=60)
            slot_date = slot_start.date()
            
            does_overlap = False
            for reservation in reservations:
                reservation_start_str = reservation['start'].get('dateTime', reservation['start'].get('date'))
                reservation_start = datetime.datetime.fromisoformat(reservation_start_str.replace('Z', '+00:00'))
                reservation_end_str = reservation['end'].get('dateTime', reservation['end'].get('date'))
                reservation_end = datetime.datetime.fromisoformat(reservation_end_str.replace('Z', '+00:00'))
                
                if slot_start < reservation_end and slot_end > reservation_start:
                    does_overlap = True
                    break
            
            if not does_overlap:
                reservation_url = f"{reverse('reserve_slot')}?{urlencode({'slot_start': slot_start.isoformat()})}"
                slots_by_date[slot_date].append({
                    'start': slot_start,
                    'reservation_url': reservation_url
                })
            
            slot_start = slot_start + datetime.timedelta(minutes=30)

    context = {
        'slots_by_date': dict(slots_by_date)
    }
    return render(request, 'app/available_slots.html', context)

def reserve_slot(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        
        if form.is_valid():
            service = get_google_calendar_service()
            slot_start = form.cleaned_data['slot_start']
            slot_end = slot_start + datetime.timedelta(minutes=60)

            # Check for conflicts
            events_result = service.events().list(
                calendarId=settings.CALENDAR_ID,
                timeMin=slot_start.isoformat(),
                timeMax=slot_end.isoformat(),
                singleEvents=True,
                orderBy='startTime',
                q='Rezervacija',
            ).execute()

            # Check whether the requested slot exists in the available slots
            available_slots_result = service.events().list(
                calendarId=settings.CALENDAR_ID,
                timeMin=slot_start.isoformat(),
                timeMax=slot_end.isoformat(),
                singleEvents=True,
                orderBy='startTime',
                q='Langas',
            ).execute()

            available_slots = available_slots_result.get('items', [])
            slot_exists = available_slots != []
            
            if not slot_exists:
                form.add_error(None, 'Pasirinktas laikas nėra galimas.')

            conflicting_events = events_result.get('items', [])
            if conflicting_events:
                form.add_error(None, 'Pasirinktas laikas jau rezervuotas.')

            if form.is_valid():
                event = {
                    'summary': 'Rezervacija',
                    'description': (
                        f"Paslauga: {form.cleaned_data['service']}\n"
                        f"Vardas: {form.cleaned_data['name']}\n"
                        f"El. paštas: {form.cleaned_data['email']}\n"
                        f"Telefonas: {form.cleaned_data['phone']}\n"
                        f"Vaiko vardas: {form.cleaned_data['child_name']}\n"
                        f"Vaiko amžius: {form.cleaned_data['child_age']}\n"
                        f"Miestas: {form.cleaned_data['city']}\n"
                        f"Pastabos: {form.cleaned_data['comment']}"
                    ),
                    'start': {
                        'dateTime': slot_start.isoformat(),
                        'timeZone': 'UTC',
                    },
                    'end': {
                        'dateTime': slot_end.isoformat(),
                        'timeZone': 'UTC',
                    },
                }
                event = service.events().insert(calendarId=settings.CALENDAR_ID, body=event).execute()
                return redirect('available_slots')
    else:
        slot_start = request.GET.get('slot_start')
        form = ReservationForm(initial={'slot_start': slot_start})

    slot_start = request.GET.get('slot_start')

    context = {
        'form': form,
        'slot_start': datetime.datetime.fromisoformat(slot_start.replace('Z', '+00:00')) if slot_start else None
    }
    return render(request, 'app/reserve_slot.html', context)