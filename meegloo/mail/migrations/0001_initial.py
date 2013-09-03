# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MailType'
        db.create_table('mail_type', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('can_unsubscribe', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('mail', ['MailType'])

        # Adding model 'Message'
        db.create_table('mail_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('kind', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', to=orm['mail.MailType'])),
            ('filter_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('filter_lurkers', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('filter_cold', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('filter_freezing', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('filter_noprofile', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('subject_template', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('header_template', self.gf('django.db.models.fields.TextField')()),
            ('footer_template', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('sent', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('mail', ['Message'])

        # Adding M2M table for field exclude_messages on 'Message'
        db.create_table('mail_message_exclude', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_message', models.ForeignKey(orm['mail.message'], null=False)),
            ('to_message', models.ForeignKey(orm['mail.message'], null=False))
        ))
        db.create_unique('mail_message_exclude', ['from_message_id', 'to_message_id'])

        # Adding model 'Section'
        db.create_table('mail_section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sections', to=orm['mail.Message'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('title_template', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('body_template', self.gf('django.db.models.fields.TextField')()),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('mail', ['Section'])

        # Adding model 'Recipient'
        db.create_table('mail_recipient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recipients', to=orm['mail.Message'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', to=orm['auth.User'])),
            ('sent', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('test', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('mail', ['Recipient'])

        # Adding model 'Unsubscribe'
        db.create_table('mail_unsubscribe', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('kind', self.gf('django.db.models.fields.related.ForeignKey')(related_name='unsubscribes', to=orm['mail.MailType'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='unsubscribes', to=orm['auth.User'])),
            ('unsubscribed', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('mail', ['Unsubscribe'])


    def backwards(self, orm):
        
        # Deleting model 'MailType'
        db.delete_table('mail_type')

        # Deleting model 'Message'
        db.delete_table('mail_message')

        # Removing M2M table for field exclude_messages on 'Message'
        db.delete_table('mail_message_exclude')

        # Deleting model 'Section'
        db.delete_table('mail_section')

        # Deleting model 'Recipient'
        db.delete_table('mail_recipient')

        # Deleting model 'Unsubscribe'
        db.delete_table('mail_unsubscribe')


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
        'mail.mailtype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'MailType', 'db_table': "'mail_type'"},
            'can_unsubscribe': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'mail.message': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Message'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'exclude_messages': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'exclude_messages_rel_+'", 'null': 'True', 'db_table': "'mail_message_exclude'", 'to': "orm['mail.Message']"}),
            'filter_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'filter_cold': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_freezing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_lurkers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_noprofile': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'footer_template': ('django.db.models.fields.TextField', [], {}),
            'header_template': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['mail.MailType']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'subject_template': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'mail.recipient': {
            'Meta': {'ordering': "('-sent',)", 'object_name': 'Recipient'},
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recipients'", 'to': "orm['mail.Message']"}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'test': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['auth.User']"})
        },
        'mail.section': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Section'},
            'body_template': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections'", 'to': "orm['mail.Message']"}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'title_template': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'mail.unsubscribe': {
            'Meta': {'ordering': "('-unsubscribed',)", 'object_name': 'Unsubscribe'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'unsubscribes'", 'to': "orm['mail.MailType']"}),
            'unsubscribed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'unsubscribes'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['mail']
