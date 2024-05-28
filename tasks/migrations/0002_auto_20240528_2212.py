# Generated by Django 5.0.6 on 2024-05-28 22:12

from django.db import migrations


def create_initial_priorities(apps, schema_editor):
    Priority = apps.get_model('tasks', 'Priority')
    
    # Crea registros de prioridad inicial
    Priority.objects.create(name='Prioridad 1')
    Priority.objects.create(name='Prioridad 2')
    Priority.objects.create(name='Prioridad 3')

class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_priorities),
    ]
