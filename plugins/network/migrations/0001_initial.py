# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Gateway'
        db.create_table('network_gateway', (
            ('server_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['resources.Server'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('network', ['Gateway'])


    def backwards(self, orm):
        # Deleting model 'Gateway'
        db.delete_table('network_gateway')


    models = {
        'network.gateway': {
            'Meta': {'object_name': 'Gateway', '_ormbases': ['resources.Server']},
            'server_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['resources.Server']", 'unique': 'True', 'primary_key': 'True'})
        },
        'project.city': {
            'Meta': {'object_name': 'City'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'project.island': {
            'Meta': {'object_name': 'Island'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.City']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'resources.server': {
            'Meta': {'object_name': 'Server'},
            'bandwidth': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'cpu': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '256', 'null': 'True'}),
            'disk': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Island']"}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'mem': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'os': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'state': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['network']