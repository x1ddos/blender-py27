# -*- coding: utf-8 -*-
import webapp2
from webapp2 import Route

import handlers

app_config = {
  'webapp2_extras.sessions': {
    'cookie_name': 'eblendr',
    # e.g. 'import os; os.urandom(64)''
    'secret_key': 'a\xa3\xee\x87\xeb\xa4\xa4\xbe\xfd\x01\xb0PG[\xe4\x1er\xb11Dg\xae\xbeGt\x9a\x87F\xb2'
  }
}

# Map URLs to handlers
routes = [
  # Pages management
  Route('/', handler='handlers.Index'),
  Route('/list', handler='handlers.Index:list'),
  Route('/event', handler='handlers.UserEvent', name='event'),
]

app = webapp2.WSGIApplication(routes, config=app_config, debug=True)
# Here's a simpler version:
# app = webapp2.WSGIApplication([
#     ('/', MainHandler)
# ], debug=True)
