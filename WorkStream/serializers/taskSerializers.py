
from rest_framework import serializers
from WorkStream.models.tasks import Task
from WorkStream.models.customUser import CustomUser
from WorkStream.models.state import State
from WorkStream.models.priority import Priority
from WorkStream.serializers import StateSerializer, PrioritySerializer, CustomUserSerializer, TaskWriteSerializer, TaskReadSerializer, LoginSerializer, CommentSerializer


class TaskReadSerializer(serializers.ModelSerializer):
    state = StateSerializer()
    priority = PrioritySerializer()
    owner = CustomUserSerializer()
    assigned_users = CustomUserSerializer(many=True)
    comment = CommentSerializer()

    class Meta:
        model = Task
        fields = '__all__'

# Serializador para la escritura
class TaskWriteSerializer(serializers.ModelSerializer):
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())
    priority = serializers.PrimaryKeyRelatedField(queryset=Priority.objects.all())
    assigned_users = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)
    comment = CommentSerializer()

    class Meta:
        model = Task
        exclude = ['owner']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['owner'] = user
        return super().create(validated_data)