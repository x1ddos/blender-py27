# -*- coding: utf-8 -*-
from google.appengine.ext import ndb

import prettydates

def human_date(date):
  if date:
    return prettydates.date(date)

def formatted_date(date):
  if date:
    return date.strftime("%a, %d %b %Y at %H:%M %z")

class Event(ndb.Model):
  """Event class that rapresent Datastore entities of Event kind"""
  title = ndb.StringProperty(required=True)
  start = ndb.DateTimeProperty(required=True)
  end = ndb.DateTimeProperty()
  place = ndb.StringProperty(indexed=False)
  desc = ndb.TextProperty()
  links = ndb.StringProperty(repeated=True)
  updated = ndb.DateTimeProperty(auto_now=True)

  @classmethod
  def list(cls):
    """Returns a list of all Events ordered by start date"""
    return cls.query().order(cls.start).fetch()

  @property
  def human_start(self):
    return human_date(self.start)

  @property
  def human_end(self):
    return human_date(self.end)

  @property
  def formatted_start(self):
    return formatted_date(self.start)

  @property
  def formatted_end(self):
    return formatted_date(self.end)
