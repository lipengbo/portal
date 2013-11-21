# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DailyCounter'
        db.create_table('common_dailycounter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target', self.gf('django.db.models.fields.IntegerField')()),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('common', ['DailyCounter'])

        # Adding unique constraint on 'DailyCounter', fields ['target', 'date']
        db.create_unique('common_dailycounter', ['target', 'date'])


    def backwards(self, orm):
        # Removing unique constraint on 'DailyCounter', fields ['target', 'date']
        db.delete_unique('common_dailycounter', ['target', 'date'])

        # Deleting model 'DailyCounter'
        db.delete_table('common_dailycounter')


    models = {
        'common.dailycounter': {
            'Meta': {'unique_together': "(('target', 'date'),)", 'object_name': 'DailyCounter'},
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'target': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['common']