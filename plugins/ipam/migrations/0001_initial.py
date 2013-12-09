# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Network'
        db.create_table('ipam_network', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('netaddr', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('ipam', ['Network'])

        # Adding model 'Subnet'
        db.create_table('ipam_subnet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('supernet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ipam.Network'])),
            ('netaddr', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('owner', self.gf('django.db.models.fields.CharField')(max_length=60, unique=True, null=True)),
            ('is_owned', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_used', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('update_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('ipam', ['Subnet'])

        # Adding model 'IPUsage'
        db.create_table('ipam_ipusage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('supernet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ipam.Subnet'])),
            ('ipaddr', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('is_used', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ipam', ['IPUsage'])


    def backwards(self, orm):
        # Deleting model 'Network'
        db.delete_table('ipam_network')

        # Deleting model 'Subnet'
        db.delete_table('ipam_subnet')

        # Deleting model 'IPUsage'
        db.delete_table('ipam_ipusage')


    models = {
        'ipam.ipusage': {
            'Meta': {'ordering': "['id']", 'object_name': 'IPUsage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipaddr': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'is_used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'supernet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ipam.Subnet']"})
        },
        'ipam.network': {
            'Meta': {'ordering': "['id']", 'object_name': 'Network'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'netaddr': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'ipam.subnet': {
            'Meta': {'ordering': "['id']", 'object_name': 'Subnet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_owned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'netaddr': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'owner': ('django.db.models.fields.CharField', [], {'max_length': '60', 'unique': 'True', 'null': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'supernet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ipam.Network']"}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ipam']