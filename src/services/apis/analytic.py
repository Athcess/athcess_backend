from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from django.http import JsonResponse
from rest_framework import viewsets, status, permissions, serializers
from ..models.blob_storage import BlobStorage
from ..models.physical_attribute import PhysicalAttribute
from ..utils.analytic.situp import *
from ..utils.analytic.sprint import *
from ..utils.analytic.pushup import *

class BlobStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlobStorage
        fields = '__all__'

class PhysicalAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalAttribute
        fields = ['created_at', 'username', 'sit_up', 'push_up', 'run']

class AnalyticsViewSet(viewsets.ModelViewSet):
    queryset = BlobStorage.objects.all()
    serializer_class = BlobStorageSerializer

    def get_analytics(self, request, *args, **kwargs):
        username = request.query_params.get('player_name')
        physical_attribute_type = request.query_params.get('analytic_type')
        height = request.query_params.get('height')
        if not height:
            height = 0
        else:
            height = int(height)

        # Get blobstorage with latest date
        blobstorage = BlobStorage.objects.filter(
            username=username, 
            physical_attribute_type=physical_attribute_type
        ).latest('created_at')

        url = blobstorage.url

        if physical_attribute_type == 'sit_up':
            count = count_situps(url)
            physical_attribute = {
                'created_at': timezone.now(),
                'username': username,
                'sit_up': count,
            }
            serializer = PhysicalAttributeSerializer(data=physical_attribute)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif physical_attribute_type == 'push_up':
            count = count_push_ups(url)
            physical_attribute = {
                'created_at': timezone.now(),
                'username': username,
                'push_up': count,
            }
            serializer = PhysicalAttributeSerializer(data=physical_attribute)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif physical_attribute_type == 'run':
            try:
                speed = calculate_speed(url, float(height))
                physical_attribute = {
                    'created_at': timezone.now(),
                    'username': username,
                    'run': float(speed),
                    'height': height,
                }
                serializer = PhysicalAttributeSerializer(data=physical_attribute)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'message': e}, status=status.HTTP_400_BAD_REQUEST)

        else: 
            return Response({'message': 'Invalid analytic type. There are only 3 types of analytics: sit_up, push_up, run'},status=status.HTTP_400_BAD_REQUEST)
