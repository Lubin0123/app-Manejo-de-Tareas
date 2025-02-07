from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from WorkStream.models import CustomUser, Priority, State, Task
from WorkStream.permissions import IsAuthenticatedOrReadOnly, IsOwnerOrAssignedUser
from WorkStream.serializers import TaskReadSerializer, TaskWriteSerializer


@swagger_auto_schema(
    method="get",
    operation_description="Obtiene una lista de todas las tareas.",
    responses={200: TaskReadSerializer(many=True)},
)
@swagger_auto_schema(
    method="post",
    operation_description="Crea una nueva tarea. Acepta múltiples tareas si se envía una lista.",
    request_body=TaskWriteSerializer(many=True),
    responses={201: TaskWriteSerializer(many=True), 400: "Bad Request"},
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def task_list_create(request):

    if request.method == "GET":
        tasks = Task.objects.all()
        serializer = TaskReadSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "POST":
        is_many = isinstance(request.data, list)
        serializer = TaskWriteSerializer(
            data=request.data, many=is_many, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    operation_description="Obtiene los detalles de una tarea específica.",
    responses={200: TaskReadSerializer, 404: "Not Found"},
)
@swagger_auto_schema(
    method="put",
    operation_description="Actualiza completamente una tarea específica.",
    request_body=TaskWriteSerializer,
    responses={200: TaskWriteSerializer, 400: "Bad Request", 404: "Not Found"},
)
@swagger_auto_schema(
    method="patch",
    operation_description="Actualiza parcialmente una tarea específica.",
    request_body=TaskWriteSerializer,
    responses={200: TaskWriteSerializer, 400: "Bad Request", 404: "Not Found"},
)
@swagger_auto_schema(
    method="delete",
    operation_description="Elimina una tarea específica.",
    responses={204: "No Content", 404: "Not Found"},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticatedOrReadOnly, IsOwnerOrAssignedUser])
def tasks_detail(request, pk, format=None):
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not IsOwnerOrAssignedUser().has_object_permission(request, None, task):
        return Response(
            {"detail": "You do not have permission to perform this action bro."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "GET":
        serializer = TaskReadSerializer(task)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        serializer = TaskWriteSerializer(
            task,
            data=request.data,
            partial=(request.method == "PATCH"),
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method="get",
    operation_description="Obtiene una lista de tareas filtradas por estado.",
    manual_parameters=[
        openapi.Parameter(
            "state",
            openapi.IN_QUERY,
            description="ID o nombre del estado",
            type=openapi.TYPE_STRING,
        ),
    ],
    responses={200: TaskReadSerializer(many=True), 404: "Not Found"},
)
@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def task_by_state_list(request):

    state_param = request.GET.get("state")
    if state_param:
        try:
            state = State.objects.get(pk=state_param)
        except (State.DoesNotExist, ValueError):
            try:
                state = State.objects.get(name__iexact=state_param)
            except State.DoesNotExist:
                return Response(
                    {"error": "Estado no encontrado"}, status=status.HTTP_404_NOT_FOUND
                )
        tasks = Task.objects.filter(state=state)
    else:
        tasks = Task.objects.all()

    serializer = TaskReadSerializer(tasks, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method="get",
    operation_description="Obtiene una lista de tareas filtradas por prioridad.",
    manual_parameters=[
        openapi.Parameter(
            "priority",
            openapi.IN_QUERY,
            description="ID o nombre de la prioridad",
            type=openapi.TYPE_STRING,
        ),
    ],
    responses={200: TaskReadSerializer(many=True), 404: "Not Found"},
)
@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def task_by_priority_list(request):

    priority_param = request.GET.get("priority")
    if priority_param:
        try:
            priority = Priority.objects.get(pk=priority_param)
        except (Priority.DoesNotExist, ValueError):
            try:
                priority = Priority.objects.get(name__iexact=priority_param)
            except Priority.DoesNotExist:
                return Response(
                    {"error": "Prioridad no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        tasks = Task.objects.filter(priority=priority)
    else:
        tasks = Task.objects.all()

    serializer = TaskReadSerializer(tasks, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method="get",
    operation_description="Obtiene una lista de tareas filtradas por fecha exacta, tareas antes de cierta fecha y tareas posteriores a cierta fecha.",
    manual_parameters=[
        openapi.Parameter(
            "deadline",
            openapi.IN_QUERY,
            description="Fecha que se desea buscar (formato YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            default="exact",
        ),
        openapi.Parameter(
            "filter",
            openapi.IN_QUERY,
            description="Tipo de filtro (exact, before, after)",
            type=openapi.TYPE_STRING,
        ),
    ],
    responses={200: TaskReadSerializer(many=True), 404: "Not Found"},
)
@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def task_by_deadline(request):

    deadline_param = request.GET.get("deadline")
    filter_type = request.GET.get("filter", "exact")
    if deadline_param:
        try:
            if filter_type == "before":
                tasks = Task.objects.filter(deadline__lt=deadline_param)
            elif filter_type == "after":
                tasks = Task.objects.filter(deadline__gt=deadline_param)
            else:
                tasks = Task.objects.filter(deadline=deadline_param)

        except ValueError:
            return Response(
                {"error": "No hay tarea con la fecha proporcionada"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        tasks = Task.objects.all()

    serializer = TaskReadSerializer(tasks, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method="get",
    operation_description="Obtiene una lista de tareas filtradas por dueño de la tarjeta.",
    manual_parameters=[
        openapi.Parameter(
            "owner",
            openapi.IN_QUERY,
            description="ID o nombre de usuario del dueño de la tarjeta",
            type=openapi.TYPE_STRING,
        ),
    ],
    responses={200: TaskReadSerializer(many=True), 404: "Not Found"},
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def task_by_owner(request):
    owner_param = request.GET.get("owner")
    if owner_param:
        try:
            owner = CustomUser.objects.get(pk=owner_param)
        except (CustomUser.DoesNotExist, ValueError):
            try:
                owner = CustomUser.objects.get(username=owner_param)
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": "No hay tarea con ese dueño"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        tasks = Task.objects.filter(owner=owner)
    else:
        tasks = Task.objects.all()

    serializer = TaskReadSerializer(tasks, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method="get",
    operation_description="Obtiene una lista de tareas filtradas por usuarios asignados.",
    manual_parameters=[
        openapi.Parameter(
            "assigned_users",
            openapi.IN_QUERY,
            description="ID o nombre de usuario del usuario asignado",
            type=openapi.TYPE_STRING,
        ),
    ],
    responses={200: TaskReadSerializer(many=True), 404: "Not Found"},
)
@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def task_by_assigned_users(request):
    assigned_users_param = request.GET.get("assigned_users")
    if assigned_users_param:
        try:
            assigned_users = CustomUser.objects.get(
                Q(pk=assigned_users_param) | Q(username=assigned_users_param)
            )
            tasks = Task.objects.filter(assigned_users=assigned_users)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "No hay un usuario asignado"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        tasks = Task.objects.all()

    serializer = TaskReadSerializer(tasks, many=True)
    return Response(serializer.data)
