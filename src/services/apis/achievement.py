from users.models.custom_user import CustomUser, Athlete, Scout, Admin_organization, Organization
from ..models.achievement import Achievement
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.response import Response
from django.utils import timezone
from ..utils.achievement import mock_achievement_data

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'


class AchievementViewSets(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        created_at = timezone.now()
        serializer = AchievementSerializer(data={
                                            'username': request.user,
                                            'created_at': created_at,
                                            'date': request.data['date'],
                                            'topic': request.data['topic'],
                                            'sub_topic': request.data['sub_topic'],
                                            'description': request.data['description'],
                                          })

        if not serializer.is_valid():
            print(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        for key, value in request.query_params.items():
            queryset = queryset.filter(**{key: value})
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def mock_achievements(self, num_achievements):
        achievements = mock_achievement_data(num_achievements)
        for achievement in achievements:
            serializer = AchievementSerializer(data=achievement)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

    