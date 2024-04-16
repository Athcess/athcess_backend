from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from ..models.post import Post
from ..models.event import Event
from django.utils import timezone
from ..utils.mock_event import mock_event_data
from ..utils.calendar_utils import create_calendar,append_event
from datetime import datetime
from django.http import JsonResponse

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @action(detail=False, methods=['get'], url_path='get-calendar')
    def get(self, request, *args, **kwargs):
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        calendar_data = create_calendar(year, month)
        events = Event.objects.all()
        calendar_data = append_event(calendar_data, day, events)
        return Response({"calendar": calendar_data}, status=status.HTTP_200_OK)


    def create(self, request, *args, **kwargs):
        data = {
            'event_id': request.data.get('event_id'),
            'club': request.data.get('org_name'),
            'content': request.data.get('content'),
            'created_at': timezone.now(),
        }
        event_serializer = EventSerializer(data=data)
        if event_serializer.is_valid():
            event_serializer.save()
            return Response(event_serializer.data, status=status.HTTP_201_CREATED)
        return Response(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        updated_content = request.data.get('updated_content')
        if updated_content:
            instance.content = updated_content
            instance.save()
            serializer = EventSerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'message': 'Updated Content not provided'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Event deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    def generate_mock_events(self, request, *args, **kwargs):
        num_events = request.data.get('num_events', 10) 
        events_data = mock_event_data(num_events=num_events)
        created_events = []
        for event_data in events_data:
            event = Event.objects.create(
                club=event_data.club,
                content=event_data.content,
                created_at=event_data.created_at,
                like=event_data.like
            )
            created_events.append(event)
        
        return Response({'message': f'{num_events} mock events created successfully'}, status=status.HTTP_201_CREATED)