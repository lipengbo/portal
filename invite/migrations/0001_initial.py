# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Invitation'
        db.create_table('invite_invitation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invite_invitation_from_invitations', to=orm['auth.User'])),
            ('to_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invite_invitation_to_invitations', to=orm['auth.User'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('target_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('target_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('invite', ['Invitation'])

        # Adding model 'Application'
        db.create_table('invite_application', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invite_application_from_invitations', to=orm['auth.User'])),
            ('to_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invite_application_to_invitations', to=orm['auth.User'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('target_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('target_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('invite', ['Application'])


    def backwards(self, orm):
        # Deleting model 'Invitation'
        db.delete_table('invite_invitation')

        # Deleting model 'Application'
        db.delete_table('invite_application')


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
        'invite.application': {
            'Meta': {'object_name': 'Application'},
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invite_application_from_invitations'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'target_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'target_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invite_application_to_invitations'", 'to': "orm['auth.User']"})
        },
        'invite.invitation': {
            'Meta': {'object_name': 'Invitation'},
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invite_invitation_from_invitations'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'target_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'target_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invite_invitation_to_invitations'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['invite']