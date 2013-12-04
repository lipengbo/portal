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
            ('gw_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('gw_mac', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('island', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['project.Island'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('ipam', ['Network'])

        # Adding unique constraint on 'Network', fields ['island', 'type']
        db.create_unique('ipam_network', ['island_id', 'type'])

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
        # Removing unique constraint on 'Network', fields ['island', 'type']
        db.delete_unique('ipam_network', ['island_id', 'type'])

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
            'Meta': {'ordering': "['id']", 'unique_together': "(('island', 'type'),)", 'object_name': 'Network'},
            'gw_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'gw_mac': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['project.Island']", 'null': 'True', 'blank': 'True'}),
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
        }
    }

    complete_apps = ['ipam']