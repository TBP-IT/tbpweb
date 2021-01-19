# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SyllabusCandidateRequirement'
        db.create_table(u'candidates_syllabuscandidaterequirement', (
            (u'candidaterequirement_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['candidates.CandidateRequirement'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'candidates', ['SyllabusCandidateRequirement'])


    def backwards(self, orm):
        # Deleting model 'SyllabusCandidateRequirement'
        db.delete_table(u'candidates_syllabuscandidaterequirement')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'base.term': {
            'Meta': {'ordering': "('id',)", 'unique_together': "(('term', 'year'),)", 'object_name': 'Term'},
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'year': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'candidates.candidate': {
            'Meta': {'ordering': "('-term', 'user__userprofile')", 'unique_together': "(('user', 'term'),)", 'object_name': 'Candidate'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['base.Term']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'candidates.candidaterequirement': {
            'Meta': {'ordering': "('-term', 'requirement_type')", 'object_name': 'CandidateRequirement'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credits_needed': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requirement_type': ('django.db.models.fields.CharField', [], {'max_length': '9', 'db_index': 'True'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['base.Term']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'candidates.candidaterequirementprogress': {
            'Meta': {'ordering': "('requirement', 'candidate')", 'object_name': 'CandidateRequirementProgress'},
            'alternate_credits_needed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['candidates.Candidate']"}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manually_recorded_credits': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'requirement': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['candidates.CandidateRequirement']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'candidates.challenge': {
            'Meta': {'ordering': "('candidate', 'created')", 'object_name': 'Challenge'},
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['candidates.Candidate']"}),
            'challenge_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['candidates.ChallengeType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'verified': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'verifying_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'candidates.challengecandidaterequirement': {
            'Meta': {'ordering': "('-term', 'requirement_type', 'challenge_type')", 'object_name': 'ChallengeCandidateRequirement', '_ormbases': [u'candidates.CandidateRequirement']},
            u'candidaterequirement_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['candidates.CandidateRequirement']", 'unique': 'True', 'primary_key': 'True'}),
            'challenge_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['candidates.ChallengeType']"})
        },
        u'candidates.challengetype': {
            'Meta': {'object_name': 'ChallengeType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'})
        },
        u'candidates.eventcandidaterequirement': {
            'Meta': {'ordering': "('-term', 'requirement_type', 'event_type')", 'object_name': 'EventCandidateRequirement', '_ormbases': [u'candidates.CandidateRequirement']},
            u'candidaterequirement_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['candidates.CandidateRequirement']", 'unique': 'True', 'primary_key': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.EventType']"})
        },
        u'candidates.examfilecandidaterequirement': {
            'Meta': {'ordering': "('-term', 'requirement_type')", 'object_name': 'ExamFileCandidateRequirement', '_ormbases': [u'candidates.CandidateRequirement']},
            u'candidaterequirement_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['candidates.CandidateRequirement']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'candidates.manualcandidaterequirement': {
            'Meta': {'ordering': "('-term', 'requirement_type', 'name')", 'object_name': 'ManualCandidateRequirement', '_ormbases': [u'candidates.CandidateRequirement']},
            u'candidaterequirement_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['candidates.CandidateRequirement']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'db_index': 'True'})
        },
        u'candidates.resumecandidaterequirement': {
            'Meta': {'ordering': "('-term', 'requirement_type')", 'object_name': 'ResumeCandidateRequirement', '_ormbases': [u'candidates.CandidateRequirement']},
            u'candidaterequirement_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['candidates.CandidateRequirement']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'candidates.syllabuscandidaterequirement': {
            'Meta': {'ordering': "('-term', 'requirement_type')", 'object_name': 'SyllabusCandidateRequirement', '_ormbases': [u'candidates.CandidateRequirement']},
            u'candidaterequirement_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['candidates.CandidateRequirement']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'events.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'eligible_elective': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'})
        }
    }

    complete_apps = ['candidates']