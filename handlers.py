# -*- coding: utf-8 -*-
import os
import logging

import webapp2
from webapp2_extras import sessions, jinja2
from jinja2.runtime import TemplateNotFound

import parsedatetime.parsedatetime as pdt
import parsedatetime.parsedatetime_consts as pdc
from time import mktime
from datetime import datetime

import models

# See this on Jinja2 templates:
# http://jinja.pocoo.org/docs/templates

class BaseHandler(webapp2.RequestHandler):
  """Base class for all frontend request handlers"""
  def dispatch(self):
    # Get a session store for this request.
    self.session_store = sessions.get_store(request=self.request)
    
    try:
      # Dispatch the request.
      webapp2.RequestHandler.dispatch(self)
    finally:
      # Save all sessions.
      self.session_store.save_sessions(self.response)
  
  @webapp2.cached_property    
  def jinja2(self):
    """Returns a Jinja2 renderer cached in the app registry"""
    return jinja2.get_jinja2(app=self.app)
    
  @webapp2.cached_property
  def session(self):
    """Returns a session using the default cookie key"""
    return self.session_store.get_session()
      
  def render(self, template_name, **template_vars):
    # Preset values for the template
    values = {
      'url_for'    : self.uri_for
    }    
    # Add manually supplied template values
    values.update(template_vars)
    
    # Set headers
    self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
    
    # read the template or 404.html
    try:
      self.response.write(self.jinja2.render_template(template_name, **values))
    except TemplateNotFound:
      self.error(404)
      values.update(title='Not found')
      self.response.write(self.jinja2.render_template(
        'notfound.html', **values))

class Index(BaseHandler):
  """Homepage handler"""
  def get(self):
    self.render('index.html')

  def list(self):
    events = models.Event.list()
    self.render('list.html', events_list=events)

class UserEvent(BaseHandler):
  """Handles event management by users"""
  def get(self):
    """Handles GET /event?id=123"""
    eventId = self.request.get('id')
    try:
      eventId = int(eventId)
    except ValueError, e:
      pass

    if not eventId:
      self.render('add.html', title='Add a new event', event=None)
      return

    event = models.Event.get_by_id(eventId)
    if not event:
      self.render('notfound.html', title='Event not found')
      return

    if self.request.get('edit'):
      self.render('edit.html', title='Edit event', event=event)
    else:
      eventUrl = self.uri_for('event', id=eventId, _full=True)
      qrimage = qrcode_image_url(eventUrl)
      self.render('event.html',
        title=event.title, event=event, qr_image_url=qrimage)

  def post(self):
    """Handles POST /event"""
    try:
      eventId = int(self.request.get('id'))
      self._update(eventId)
    except ValueError:
      self._create()

  def _update(self, eventId):
    """Updates existing event"""
    event = models.Event.get_by_id(eventId)
    props = self._event_props_from_request()
    props.pop('id', None)
    event.populate(**props)
    key = event.put()
    self.redirect('/event?id=%d' % key.integer_id())

  def _create(self):
    """Creates a new event"""
    event = models.Event(**self._event_props_from_request())
    key = event.put()
    self.redirect('/event?id=%d' % key.integer_id())

  def _event_props_from_request(self):
    c = pdc.Constants("en")
    p = pdt.Calendar(c)
    startDate, _, = p.parse(self.request.get('start'))
    startDate = datetime.fromtimestamp(mktime(startDate))
    endDate, _, = p.parse(self.request.get('end'))
    endDate = datetime.fromtimestamp(mktime(endDate))
    return {
      'title': self.request.get('title'),
      'start': startDate,
      'end': endDate,
      'place': self.request.get('place'),
      'desc': self.request.get('description')
    }


def qrcode_image_url(origin):
  return 'https://chart.googleapis.com/chart?%s' % '&'.join([
    'cht=qr', 'chs=150x150', 'chld=H|0', 'chl=%s' % origin
    ])
