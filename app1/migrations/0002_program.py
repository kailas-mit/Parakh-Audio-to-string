# Generated by Django 4.1.7 on 2023-04-19 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.CharField(choices=[('General Program', 'General Program'), ('AOP Program', 'AOP Program')], max_length=50)),
            ],
        ),
    ]
