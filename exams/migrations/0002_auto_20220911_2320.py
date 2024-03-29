# Generated by Django 2.2.8 on 2022-09-12 06:20

import course_files.models
from django.db import migrations
import private_storage.fields
import private_storage.storage.files


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='exam_file',
            field=private_storage.fields.PrivateFileField(storage=private_storage.storage.files.PrivateFileSystemStorage(), upload_to=course_files.models.generate_courseitem_filepath),
        ),
    ]
