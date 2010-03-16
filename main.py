from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api import memcache

import os
from google.appengine.ext.webapp import template
from bloom import Bloom


class MainHandler(webapp.RequestHandler):
  def get(self):
    try:
      status = self.request.GET["success"]
      value = self.request.GET["value"]
    except KeyError:
      status = None
      value = None

    template_values = {
        'status'  : status,
        'value'   : value
    }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):
    bloom = memcache.get("filter")
    if bloom is None:
      bloom = Bloom(2**21, 5)
    
    value = self.request.POST["value"]
    value_already_included = False
    if value in bloom:
      value_already_included = True
    bloom.add(value)
    memcache.set("filter", bloom)
    self.redirect("/?success=" + str(not value_already_included) 
                  + "&value=" + value)
                  

class FlushCacheHandler(webapp.RequestHandler):
  def post(self):
    memcache.flush_all()
    self.redirect("/")

application = webapp.WSGIApplication([ 
                                      ('/', MainHandler),
                                      ('/flush', FlushCacheHandler),
                                     ], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
