# sitemaps.py
from django.contrib import sitemaps
from django.core.urlresolvers import reverse
from collections import OrderedDict

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
      return list(self.itemnames(self).keys())

    def itemnames(self):
        return OrderedDict([
          ('index', 'Homepagina'),
          ('kerktijden', 'Kerktijden'),
          ('kindercreche', 'Kindercrèche'),
          ('orgel', 'Orgel'),
          ('anbi', 'ANBI gegevens'),
        ])

    def location(self, item):
        return reverse(item)
