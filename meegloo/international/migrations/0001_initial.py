# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Currency'
        db.create_table('international_currency', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('symbol', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal('international', ['Currency'])

        # Adding model 'Country'
        db.create_table('international_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(related_name='countries', to=orm['international.Currency'])),
        ))
        db.send_create_signal('international', ['Country'])

        # Adding model 'TimeZone'
        db.create_table('international_timezone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('offset_hours', self.gf('django.db.models.fields.IntegerField')()),
            ('offset_minutes', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('international', ['TimeZone'])


    def backwards(self, orm):
        
        # Deleting model 'Currency'
        db.delete_table('international_currency')

        # Deleting model 'Country'
        db.delete_table('international_country')

        # Deleting model 'TimeZone'
        db.delete_table('international_timezone')


    models = {
        'international.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'countries'", 'to': "orm['international.Currency']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'international.currency': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Currency'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        'international.timezone': {
            'Meta': {'ordering': "('offset_hours', 'offset_minutes')", 'object_name': 'TimeZone'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'offset_hours': ('django.db.models.fields.IntegerField', [], {}),
            'offset_minutes': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['international']
