# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Flowvisor.content_type'
        db.delete_column('openflow_flowvisor', 'content_type_id')

        # Deleting field 'Flowvisor.object_id'
        db.delete_column('openflow_flowvisor', 'object_id')


    def backwards(self, orm):
        # Adding field 'Flowvisor.content_type'
        db.add_column('openflow_flowvisor', 'content_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Flowvisor.object_id'
        db.add_column('openflow_flowvisor', 'object_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'openflow.controller': {
            'Meta': {'object_name': 'Controller'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'is_root': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Island']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'slices': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['slice.Slice']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'openflow.flowspacerule': {
            'Meta': {'object_name': 'FlowSpaceRule'},
            'actions': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'dl_dst': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'dl_src': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'dl_type': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'dl_vlan': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'dl_vpcp': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_port': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'is_default': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'nw_dst': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'nw_proto': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'nw_src': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'nw_tos': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slice.Slice']"}),
            'switch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.Switch']", 'null': 'True'}),
            'tp_dst': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'tp_src': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'openflow.flowvisor': {
            'Meta': {'object_name': 'Flowvisor'},
            'http_port': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Island']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slices': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['slice.Slice']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'openflow.flowvisorlinksmd5': {
            'Meta': {'object_name': 'FlowvisorLinksMd5'},
            'flowvisor': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['openflow.Flowvisor']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'openflow.link': {
            'Meta': {'object_name': 'Link'},
            'flowvisor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['openflow.Flowvisor']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source_links'", 'to': "orm['resources.SwitchPort']"}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'target_links'", 'to': "orm['resources.SwitchPort']"})
        },
        'project.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.CharField', [], {'default': "'img/cat_other.png'", 'max_length': '32'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
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
        'project.membership': {
            'Meta': {'unique_together': "(('project', 'user'),)", 'object_name': 'Membership'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_owner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'project.project': {
            'Meta': {'object_name': 'Project'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Category']"}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'islands': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project.Island']", 'symmetrical': 'False'}),
            'memberships': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'project_belongs'", 'symmetrical': 'False', 'through': "orm['project.Membership']", 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'resources.sliceport': {
            'Meta': {'unique_together': "(('slice', 'switch_port'),)", 'object_name': 'SlicePort'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slice.Slice']"}),
            'switch_port': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.SwitchPort']"})
        },
        'resources.sliceswitch': {
            'Meta': {'unique_together': "(('slice', 'switch'),)", 'object_name': 'SliceSwitch'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slice.Slice']"}),
            'switch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.Switch']"})
        },
        'resources.switch': {
            'Meta': {'object_name': 'Switch'},
            'dpid': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'has_gre_tunnel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Island']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slices': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['slice.Slice']", 'through': "orm['resources.SliceSwitch']", 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'resources.switchport': {
            'Meta': {'unique_together': "(('switch', 'port'),)", 'object_name': 'SwitchPort'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'slices': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['slice.Slice']", 'symmetrical': 'False', 'through': "orm['resources.SlicePort']", 'blank': 'True'}),
            'switch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.Switch']"})
        },
        'slice.slice': {
            'Meta': {'object_name': 'Slice'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_expired': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'islands': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project.Island']", 'through': "orm['slice.SliceIsland']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'show_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'slice.sliceisland': {
            'Meta': {'unique_together': "(('slice', 'island'),)", 'object_name': 'SliceIsland'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Island']"}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slice.Slice']"})
        }
    }

    complete_apps = ['openflow']