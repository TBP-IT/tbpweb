# Generated by Django 2.2.8 on 2021-09-22 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PastPresident',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('term', models.CharField(help_text='Spring 1950 or 1930-1931 or Fall 1967 - Spring 1968', max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('bio', models.TextField(blank=True, help_text='Shows up on the index page')),
                ('picture', models.ImageField(blank=True, upload_to='images/past_pres/')),
                ('title', models.CharField(blank=True, help_text='Ex: Building On Foundations - Jo Kay Chan - Spring 1999', max_length=200)),
                ('summary', models.TextField(blank=True, help_text='Quick summary of status of the chapter and future vision')),
                ('body', models.TextField(blank=True, help_text='Main multi-paragraph text')),
                ('contributions', models.TextField(blank=True, help_text='Use markdown syntax with asterisks for bullets in list')),
                ('ordering_number', models.IntegerField(blank=True, db_index=True, help_text='Number used to order presidents. Higher numbers for more recent presidents')),
            ],
            options={
                'ordering': ('-ordering_number',),
            },
        ),
    ]