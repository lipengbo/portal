# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Image'
        db.create_table('vt_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('type', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=36, null=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=36, null=True)),
            ('os', self.gf('django.db.models.fields.CharField')(max_length=256, null=True)),
        ))
        db.send_create_signal('vt', ['Image'])

        # Adding model 'Flavor'
        db.create_table('vt_flavor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('cpu', self.gf('django.db.models.fields.IntegerField')()),
            ('ram', self.gf('django.db.models.fields.IntegerField')()),
            ('hdd', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('vt', ['Flavor'])

        # Adding model 'VirtualMachine'
        db.create_table('vt_virtualmachine', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('island', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.Island'])),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, unique=True, null=True)),
            ('ip', self.gf('django.db.models.fields.related.ForeignKey')(related_name='virtualmachine_set', null=True, to=orm['ipam.IPUsage'])),
            ('gateway_public_ip', self.gf('django.db.models.fields.related.ForeignKey')(related_name='gateway_set', null=True, to=orm['ipam.IPUsage'])),
            ('mac', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('enable_dhcp', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('slice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slice.Slice'])),
            ('flavor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vt.Flavor'])),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vt.Image'])),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['resources.Server'])),
            ('switch_port', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['resources.SwitchPort'], null=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('vt', ['VirtualMachine'])

        # Adding model 'HostMac'
        db.create_table('vt_hostmac', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mac', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('host_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('host_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('vt', ['HostMac'])


    def backwards(self, orm):
        # Deleting model 'Image'
        db.delete_table('vt_image')

        # Deleting model 'Flavor'
        db.delete_table('vt_flavor')

        # Deleting model 'VirtualMachine'
        db.delete_table('vt_virtualmachine')

        # Deleting model 'HostMac'
        db.delete_table('vt_hostmac')


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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'islands': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project.Island']", 'symmetrical': 'False'}),
            'memberships': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'project_belongs'", 'symmetrical': 'False', 'through': "orm['project.Membership']", 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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
            'http_port': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Island']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
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
        },
        'vt.flavor': {
            'Meta': {'object_name': 'Flavor'},
            'cpu': ('django.db.models.fields.IntegerField', [], {}),
            'hdd': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'ram': ('django.db.models.fields.IntegerField', [], {})
        },
        'vt.hostmac': {
            'Meta': {'object_name': 'HostMac'},
            'host_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'host_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'vt.image': {
            'Meta': {'object_name': 'Image'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'os': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'})
        },
        'vt.virtualmachine': {
            'Meta': {'object_name': 'VirtualMachine'},
            'enable_dhcp': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'flavor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vt.Flavor']"}),
            'gateway_public_ip': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'gateway_set'", 'null': 'True', 'to': "orm['ipam.IPUsage']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vt.Image']"}),
            'ip': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'virtualmachine_set'", 'null': 'True', 'to': "orm['ipam.IPUsage']"}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Island']"}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.Server']"}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slice.Slice']"}),
            'state': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'switch_port': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.SwitchPort']", 'null': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True'})
        }
    }

    complete_apps = ['vt']