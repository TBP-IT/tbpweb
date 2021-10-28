# Generated by Django 2.2.8 on 2021-09-22 22:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OfficerPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=16, unique=True)),
                ('long_name', models.CharField(max_length=64, unique=True)),
                ('executive', models.BooleanField(default=False, help_text='Is this an executive position (like President)?')),
                ('auxiliary', models.BooleanField(default=False, help_text='Is this position auxiliary (i.e., not a core officer position)?')),
                ('mailing_list', models.CharField(blank=True, help_text='The mailing list name, not including the @domain.', max_length=16)),
                ('rank', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
            options={
                'ordering': ('rank',),
            },
        ),
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=8, unique=True)),
                ('long_name', models.CharField(max_length=64)),
                ('website', models.URLField()),
            ],
            options={
                'ordering': ('long_name',),
                'verbose_name_plural': 'universities',
            },
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('term', models.CharField(choices=[('un', 'Unknown'), ('wi', 'Winter'), ('sp', 'Spring'), ('su', 'Summer'), ('fa', 'Fall')], max_length=2)),
                ('year', models.PositiveSmallIntegerField()),
                ('current', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('id',),
                'unique_together': {('term', 'year')},
            },
        ),
        migrations.CreateModel(
            name='Officer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_chair', models.BooleanField(default=False, help_text='Is this person the chair of their committee?')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.OfficerPosition')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Term')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'position', 'term')},
                'permissions': (('view_officer_contacts', 'Can view officer contact information'),),
            },
        ),
        migrations.CreateModel(
            name='Major',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=8)),
                ('long_name', models.CharField(max_length=64)),
                ('is_eligible', models.BooleanField(default=False)),
                ('website', models.URLField()),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.University')),
            ],
            options={
                'ordering': ('long_name',),
                'unique_together': {('university', 'short_name')},
            },
        ),
    ]