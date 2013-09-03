#!/usr/bin/env python
# encoding: utf-8

from django.dispatch import Signal

upload_received = Signal(providing_args = ['data'])