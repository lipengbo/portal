# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DeletedCounter'
        db.create_table('common_deletedcounter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target', self.gf('django.db.models.fields.IntegerField')()),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('common', ['DeletedCounter'])

        # Adding unique constraint on 'DeletedCounter', fields ['target', 'date', 'type']
        db.create_unique('common_deletedcounter', ['target', 'date', 'type'])

        # Adding model 'FailedCounter'
        db.create_table('common_failedcounter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target', self.gf('django.db.models.fields.IntegerField')()),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('common', ['FailedCounter'])

        # Adding unique constraint on 'FailedCounter', fields ['target', 'date', 'type']
        db.create_unique('common_failedcounter', ['target', 'date', 'type'])


    def backwards(self, orm):
        # Removing unique constraint on 'FailedCounter', fields ['target', 'date', 'type']
        db.delete_unique('common_failedcounter', ['target', 'date', 'type'])

        # Removing unique constraint on 'DeletedCounter', fields ['target', 'date', 'type']
        db.delete_unique('common_deletedcounter', ['target', 'date', 'type'])

        # Deleting model 'DeletedCounter'
        db.delete_table('common_deletedcounter')

        # Deleting model 'FailedCounter'
        db.delete_table('common_failedcounter')


    models = {
        'common.counter': {
            'Meta': {'unique_together': "(('target', 'date', 'type'),)", 'object_name': 'Counter'},
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'target': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'common.deletedcounter': {
            'Meta': {'unique_together': "(('target', 'date', 'type'),)", 'object_name': 'DeletedCounter'},
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'target': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'common.failedcounter': {
            'Meta': {'unique_together': "(('target', 'date', 'type'),)", 'object_name': 'FailedCounter'},
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'target': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['common']