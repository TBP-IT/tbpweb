# Generated by Django 2.2.8 on 2021-09-22 22:27

import candidates.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initiated', models.BooleanField(default=False)),
                ('photo', models.ImageField(blank=True, upload_to=candidates.models.Candidate.rename_photo)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('term', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Term')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-term', 'user__userprofile'),
                'unique_together': {('user', 'term')},
                'permissions': (('can_initiate_candidates', 'Can mark candidates as initiated'),),
            },
        ),
        migrations.CreateModel(
            name='CandidateRequirement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requirement_type', models.CharField(choices=[('event', 'Event'), ('challenge', 'Challenge'), ('exam', 'Exam File'), ('syllabus', 'Syllabus'), ('resume', 'Resume'), ('manual', 'Other (manually verified)')], db_index=True, max_length=9)),
                ('credits_needed', models.IntegerField(help_text='Amount of credits needed to fulfill a candidate requirement')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('term', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Term')),
            ],
            options={
                'ordering': ('-term', 'requirement_type'),
            },
        ),
        migrations.CreateModel(
            name='ChallengeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExamFileCandidateRequirement',
            fields=[
                ('candidaterequirement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='candidates.CandidateRequirement')),
            ],
            bases=('candidates.candidaterequirement',),
        ),
        migrations.CreateModel(
            name='ManualCandidateRequirement',
            fields=[
                ('candidaterequirement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='candidates.CandidateRequirement')),
                ('name', models.CharField(db_index=True, max_length=60)),
            ],
            options={
                'ordering': ('-term', 'requirement_type', 'name'),
            },
            bases=('candidates.candidaterequirement',),
        ),
        migrations.CreateModel(
            name='ResumeCandidateRequirement',
            fields=[
                ('candidaterequirement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='candidates.CandidateRequirement')),
            ],
            bases=('candidates.candidaterequirement',),
        ),
        migrations.CreateModel(
            name='SyllabusCandidateRequirement',
            fields=[
                ('candidaterequirement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='candidates.CandidateRequirement')),
            ],
            bases=('candidates.candidaterequirement',),
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('verified', models.NullBooleanField(choices=[(None, 'Pending'), (True, 'Approved'), (False, 'Denied')])),
                ('reason', models.CharField(blank=True, help_text='Why is the challenge being approved or denied? (Optional)', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidates.Candidate')),
                ('challenge_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidates.ChallengeType')),
                ('verifying_user', models.ForeignKey(help_text='Person who verified the challenge.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('candidate', 'created'),
            },
        ),
        migrations.CreateModel(
            name='CandidateRequirementProgress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manually_recorded_credits', models.IntegerField(default=0, help_text='Additional credits that go toward fulfilling a candidate requirement')),
                ('alternate_credits_needed', models.IntegerField(default=0, help_text='Alternate amount of credits needed to fulfill a candidate requirement')),
                ('comments', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidates.Candidate')),
                ('requirement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidates.CandidateRequirement')),
            ],
            options={
                'ordering': ('requirement', 'candidate'),
                'verbose_name_plural': 'candidate requirement progresses',
            },
        ),
        migrations.CreateModel(
            name='EventCandidateRequirement',
            fields=[
                ('candidaterequirement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='candidates.CandidateRequirement')),
                ('event_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.EventType')),
            ],
            options={
                'ordering': ('-term', 'requirement_type', 'event_type'),
            },
            bases=('candidates.candidaterequirement',),
        ),
        migrations.CreateModel(
            name='ChallengeCandidateRequirement',
            fields=[
                ('candidaterequirement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='candidates.CandidateRequirement')),
                ('challenge_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidates.ChallengeType')),
            ],
            options={
                'ordering': ('-term', 'requirement_type', 'challenge_type'),
            },
            bases=('candidates.candidaterequirement',),
        ),
    ]
