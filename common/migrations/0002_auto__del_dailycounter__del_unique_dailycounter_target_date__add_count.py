# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'DailyCounter', fields ['target', 'date']
        db.delete_unique('common_dailycounter', ['target', 'date'])

        # Deleting model 'DailyCounter'
        db.delete_table('common_dailycounter')

        # Adding model 'Counter'
        db.create_table('common_counter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target', self.gf('django.db.models.fields.IntegerField')()),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('common', ['Counter'])

        # Adding unique constraint on 'Counter', fields ['target', 'date', 'type']
        db.create_unique('common_counter', ['target', 'date', 'type'])


    def backwards(self, orm):
        # Removing unique constraint on 'Counter', fields ['target', 'date', 'type']
        db.delete_unique('common_counter', ['target', 'date', 'type'])

        # Adding model 'DailyCounter'
        db.create_table('common_dailycounter', (
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('common', ['DailyCounter'])

        # Adding unique constraint on 'DailyCounter', fields ['target', 'date']
        db.create_unique('common_dailycounter', ['target', 'date'])

        # Deleting model 'Counter'
        db.delete_table('common_counter')


    models = {
        'common.counter': {
            'Meta': {'unique_together': "(('target', 'date', 'type'),)", 'object_name': 'Counter'},
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'target': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['common']