# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Syllabus'
        db.create_table(u'syllabi_syllabus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course_instance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['courses.CourseInstance'])),
            ('submitter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('file_ext', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('flags', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('blacklisted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('unique_id', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, blank=True)),
            ('syllabus_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'syllabi', ['Syllabus'])

        # Adding model 'SyllabusFlag'
        db.create_table(u'syllabi_syllabusflag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reason', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('resolution', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('resolved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('syllabus', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['syllabi.Syllabus'])),
        ))
        db.send_create_signal(u'syllabi', ['SyllabusFlag'])

        # Adding model 'InstructorSyllabusPermission'
        db.create_table(u'syllabi_instructorsyllabuspermission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('instructor', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['courses.Instructor'], unique=True)),
            ('permission_allowed', self.gf('django.db.models.fields.BooleanField')()),
            ('correspondence', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'syllabi', ['InstructorSyllabusPermission'])


    def backwards(self, orm):
        # Deleting model 'Syllabus'
        db.delete_table(u'syllabi_syllabus')

        # Deleting model 'SyllabusFlag'
        db.delete_table(u'syllabi_syllabusflag')

        # Deleting model 'InstructorSyllabusPermission'
        db.delete_table(u'syllabi_instructorsyllabuspermission')


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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'courses.course': {
            'Meta': {'unique_together': "(('department', 'number'),)", 'object_name': 'Course'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['courses.Department']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'courses.courseinstance': {
            'Meta': {'object_name': 'CourseInstance'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['courses.Course']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['courses.Instructor']", 'symmetrical': 'False'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['base.Term']", 'null': 'True'})
        },
        u'courses.department': {
            'Meta': {'ordering': "('long_name',)", 'object_name': 'Department'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '25'})
        },
        u'courses.instructor': {
            'Meta': {'ordering': "('last_name', 'first_name', 'middle_initial')", 'unique_together': "(('first_name', 'middle_initial', 'last_name', 'department'),)", 'object_name': 'Instructor'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['courses.Department']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'middle_initial': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'syllabi.instructorsyllabuspermission': {
            'Meta': {'ordering': "('instructor',)", 'object_name': 'InstructorSyllabusPermission'},
            'correspondence': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['courses.Instructor']", 'unique': 'True'}),
            'permission_allowed': ('django.db.models.fields.BooleanField', [], {})
        },
        u'syllabi.syllabus': {
            'Meta': {'object_name': 'Syllabus'},
            'blacklisted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'course_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['courses.CourseInstance']"}),
            'file_ext': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'flags': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submitter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'syllabus_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'unique_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'syllabi.syllabusflag': {
            'Meta': {'object_name': 'SyllabusFlag'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.TextField', [], {}),
            'resolution': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'resolved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'syllabus': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['syllabi.Syllabus']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['syllabi']