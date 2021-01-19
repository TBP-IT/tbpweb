# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AchievementIcon'
        db.create_table(u'achievements_achievementicon', (
            ('achievement', self.gf('django.db.models.fields.related.OneToOneField')(related_name='icon', unique=True, primary_key=True, to=orm['achievements.Achievement'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'achievements', ['AchievementIcon'])

        # Deleting field 'Achievement.icon_filename'
        db.delete_column(u'achievements_achievement', 'icon_filename')

        # Deleting field 'Achievement.icon_creator'
        db.delete_column(u'achievements_achievement', 'icon_creator_id')


    def backwards(self, orm):
        # Deleting model 'AchievementIcon'
        db.delete_table(u'achievements_achievementicon')

        # Adding field 'Achievement.icon_filename'
        db.add_column(u'achievements_achievement', 'icon_filename',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)

        # Adding field 'Achievement.icon_creator'
        db.add_column(u'achievements_achievement', 'icon_creator',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True),
                      keep_default=False)


    models = {
        u'achievements.achievement': {
            'Meta': {'ordering': "('rank',)", 'object_name': 'Achievement'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'goal': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manual': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'points': ('django.db.models.fields.IntegerField', [], {}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '8', 'db_index': 'True'}),
            'rank': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_index': 'True'}),
            'repeatable': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'sequence': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'})
        },
        u'achievements.achievementicon': {
            'Meta': {'object_name': 'AchievementIcon'},
            'achievement': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'icon'", 'unique': 'True', 'primary_key': 'True', 'to': u"orm['achievements.Achievement']"}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        u'achievements.userachievement': {
            'Meta': {'object_name': 'UserAchievement'},
            'achievement': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['achievements.Achievement']"}),
            'acquired': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'assigner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assigner'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'explanation': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'progress': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['base.Term']", 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
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
        u'base.term': {
            'Meta': {'ordering': "('id',)", 'unique_together': "(('term', 'year'),)", 'object_name': 'Term'},
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'year': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['achievements']