# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Network.gw_ip'
        db.add_column('ipam_network', 'gw_ip',
                      self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True),
                      keep_default=False)

        # Adding field 'Network.gw_mac'
        db.add_column('ipam_network', 'gw_mac',
                      self.gf('django.db.models.fields.CharField')(max_length=64, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Network.gw_ip'
        db.delete_column('ipam_network', 'gw_ip')

        # Deleting field 'Network.gw_mac'
        db.delete_column('ipam_network', 'gw_mac')


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
            'gw_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True'}),
            'gw_mac': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
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