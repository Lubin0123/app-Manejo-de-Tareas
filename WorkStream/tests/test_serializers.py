from rest_framework.test import APITestCase, APIRequestFactory
from WorkStream.models.tasks import Task
from WorkStream.models.state import State
from WorkStream.models.priority import Priority
from WorkStream.models.customUser import CustomUser
from WorkStream.serializers.stateSerializers import StateSerializer
from WorkStream.serializers.prioritySerializers import PrioritySerializer
from WorkStream.serializers.customUserSerializers import CustomUserSerializer
from WorkStream.serializers.taskSerializers import TaskReadSerializer, TaskWriteSerializer
from datetime import datetime

class TaskSerializerTest(APITestCase):

    def setUp(self):
        self.state = State.objects.create(name='Doing')
        self.priority = Priority.objects.create(name='Alta')
        self.user = CustomUser.objects.create_user(username='user_test', password='password')
        self.another_user = CustomUser.objects.create_user(username='anotheruser', password='password')
        self.task_data = {
            "name": "Test tarea 1",
            "description": "Este es el test de la tarea 1",
            "deadline": "2024-06-08",
            "comment": "null",
            "state": self.state.id,
            "priority": self.priority.id,
            "assigned_users": [self.user.id, self.another_user.id],
            "owner": self.user.id
        }
        self.task = Task.objects.create(
            name="Test tarea 1",
            description="Este es un test para la tarea 1",
            deadline="2024-06-08",
            comment="null",
            state=self.state,
            priority=self.priority,
            owner=self.user
        )
        self.task.assigned_users.set([self.user, self.another_user])
        self.factory = APIRequestFactory()

    def test_task_read_serializaion(self):
        serializer = TaskReadSerializer(self.task)
        data = serializer.data
        self.assertEqual(data['name'], self.task.name)
        self.assertEqual(data['description'], self.task.description)
        self.assertEqual(data['deadline'], str(self.task.deadline))
        self.assertEqual(data['comment'], self.task.comment)
        self.assertEqual(data['state']['id'], self.task.state.id)
        self.assertEqual(data['priority']['id'], self.task.priority.id)
        self.assertEqual(len(data['assigned_users']), 2)
        self.assertEqual(data['owner']['id'], self.task.owner.id)

    def test_task_write_serialization(self):
        request = self.factory.post('/tasks/', self.task_data, format='json')
        request.user = self.user
        serializer = TaskWriteSerializer(data=self.task_data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        task = serializer.save()
        self.assertEqual(task.name, self.task_data['name'])
        self.assertEqual(task.description, self.task_data['description'])
        task_deadline = datetime.strptime(self.task_data['deadline'], '%Y-%m-%d').date()
        self.assertEqual(task.deadline, task_deadline)
        self.assertEqual(task.comment, self.task_data['comment'])
        self.assertEqual(task.state.id, self.task_data['state'])
        self.assertEqual(task.priority.id, self.task_data['priority'])
        self.assertEqual(list(task.assigned_users.all()), [self.user, self.another_user])
        self.assertEqual(task.owner, self.user)