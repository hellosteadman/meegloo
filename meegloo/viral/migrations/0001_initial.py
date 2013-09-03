# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Invitation'
        db.create_table('viral_invitation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invitations', to=orm['auth.User'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('sent', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('viral', ['Invitation'])

        # Adding unique constraint on 'Invitation', fields ['sender', 'email']
        db.create_unique('viral_invitation', ['sender_id', 'email'])

        # Adding model 'Competition'
        db.create_table('viral_competition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('headline', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('subheading', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('deadline', self.gf('django.db.models.fields.DateField')()),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('terms', self.gf('django.db.models.fields.TextField')()),
            ('network', self.gf('django.db.models.fields.related.ForeignKey')(related_name='competitions', to=orm['networks.Network'])),
        ))
        db.send_create_signal('viral', ['Competition'])

        # Adding model 'Entrant'
        db.create_table('viral_entrant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entrants', to=orm['viral.Competition'])),
            ('guid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='competition_entries', to=orm['auth.User'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='subentrants', null=True, to=orm['viral.Entrant'])),
            ('barred', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('entered', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('viral', ['Entrant'])

        # Adding model 'Action'
        db.create_table('viral_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entrant', self.gf('django.db.models.fields.related.ForeignKey')(related_name='actions', to=orm['viral.Entrant'])),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('points', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='competition_actions', to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('performed', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('viral', ['Action'])

        # Adding unique constraint on 'Action', fields ['content_type', 'object_id']
        db.create_unique('viral_action', ['content_type_id', 'object_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Action', fields ['content_type', 'object_id']
        db.delete_unique('viral_action', ['content_type_id', 'object_id'])

        # Removing unique constraint on 'Invitation', fields ['sender', 'email']
        db.delete_unique('viral_invitation', ['sender_id', 'email'])

        # Deleting model 'Invitation'
        db.delete_table('viral_invitation')

        # Deleting model 'Competition'
        db.delete_table('viral_competition')

        # Deleting model 'Entrant'
        db.delete_table('viral_entrant')

        # Deleting model 'Action'
        db.delete_table('viral_action')


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
        'networks.network': {
            'Meta': {'ordering': "('-featured', 'name')", 'object_name': 'Network'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'managers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'managed_networks'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_networks'", 'to': "orm['auth.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'to': "orm['networks.SuperNetwork']"}),
            'privacy': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'networks.supernetwork': {
            'Meta': {'ordering': "('name',)", 'object_name': 'SuperNetwork'},
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'viral.action': {
            'Meta': {'ordering': "('-performed',)", 'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'Action'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'competition_actions'", 'to': "orm['contenttypes.ContentType']"}),
            'entrant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': "orm['viral.Entrant']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'performed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'points': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'viral.competition': {
            'Meta': {'ordering': "('-start',)", 'object_name': 'Competition'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'deadline': ('django.db.models.fields.DateField', [], {}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'competitions'", 'to': "orm['networks.Network']"}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'subheading': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'terms': ('django.db.models.fields.TextField', [], {})
        },
        'viral.entrant': {
            'Meta': {'ordering': "('-entered',)", 'object_name': 'Entrant'},
            'barred': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entrants'", 'to': "orm['viral.Competition']"}),
            'entered': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subentrants'", 'null': 'True', 'to': "orm['viral.Entrant']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'competition_entries'", 'to': "orm['auth.User']"})
        },
        'viral.invitation': {
            'Meta': {'ordering': "('-created',)", 'unique_together': "(('sender', 'email'),)", 'object_name': 'Invitation'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations'", 'to': "orm['auth.User']"}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        }
    }

    complete_apps = ['viral']
