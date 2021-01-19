# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Alumnus'
        db.create_table(u'alumni_alumnus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('dream', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('hobbies', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('occupation', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('college_activities', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal(u'alumni', ['Alumnus'])

        # Adding M2M table for field time_investment on 'Alumnus'
        m2m_table_name = db.shorten_name(u'alumni_alumnus_time_investment')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('alumnus', models.ForeignKey(orm[u'alumni.alumnus'], null=False)),
            ('timeinvestment', models.ForeignKey(orm[u'alumni.timeinvestment'], null=False))
        ))
        db.create_unique(m2m_table_name, ['alumnus_id', 'timeinvestment_id'])

        # Adding M2M table for field discussion_topics on 'Alumnus'
        m2m_table_name = db.shorten_name(u'alumni_alumnus_discussion_topics')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('alumnus', models.ForeignKey(orm[u'alumni.alumnus'], null=False)),
            ('discussiontopic', models.ForeignKey(orm[u'alumni.discussiontopic'], null=False))
        ))
        db.create_unique(m2m_table_name, ['alumnus_id', 'discussiontopic_id'])

        # Adding model 'DiscussionTopic'
        db.create_table(u'alumni_discussiontopic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('icon', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'alumni', ['DiscussionTopic'])

        # Adding model 'TimeInvestment'
        db.create_table(u'alumni_timeinvestment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('icon', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'alumni', ['TimeInvestment'])


    def backwards(self, orm):
        # Deleting model 'Alumnus'
        db.delete_table(u'alumni_alumnus')

        # Removing M2M table for field time_investment on 'Alumnus'
        db.delete_table(db.shorten_name(u'alumni_alumnus_time_investment'))

        # Removing M2M table for field discussion_topics on 'Alumnus'
        db.delete_table(db.shorten_name(u'alumni_alumnus_discussion_topics'))

        # Deleting model 'DiscussionTopic'
        db.delete_table(u'alumni_discussiontopic')

        # Deleting model 'TimeInvestment'
        db.delete_table(u'alumni_timeinvestment')


    models = {
        u'alumni.alumnus': {
            'Meta': {'object_name': 'Alumnus'},
            'college_activities': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'discussion_topics': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'blank': 'True', 'to': u"orm['alumni.DiscussionTopic']"}),
            'dream': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'hobbies': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'occupation': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'time_investment': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'blank': 'True', 'to': u"orm['alumni.TimeInvestment']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'alumni.discussiontopic': {
            'Meta': {'object_name': 'DiscussionTopic'},
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'alumni.timeinvestment': {
            'Meta': {'object_name': 'TimeInvestment'},
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['alumni']