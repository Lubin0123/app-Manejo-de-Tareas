# Generated by Django 5.0.6 on 2024-06-27 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkStream', '0005_alter_comment_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='full_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Nombre completo'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(null=True, unique=True),
        ),
    ]
