import django_tables2 as tables
from django.utils.safestring import mark_safe
from .models import *

class StreetZipColumn(tables.Column):
  def render(self, value):
    return mark_safe('%s <small>(%s)</small>' % (value.street, value.zip))

class ProfileTable(tables.Table):
  id = tables.Column(visible=False)
  user = tables.Column(visible=False)
  address = tables.Column(visible=False)

  first_name = tables.Column(accessor='user.first_name', verbose_name="Voornaam")
  last_name = tables.Column(accessor='user.last_name', verbose_name="Achternaam")
  email = tables.EmailColumn(accessor='user.email', verbose_name="Email")
  phone = tables.EmailColumn(verbose_name="Telefoon")
  birthday = tables.EmailColumn(verbose_name="Geboortedatum")

  street_zip = StreetZipColumn(accessor='address', verbose_name='Adres')
  city = tables.Column(accessor='address.city', verbose_name='Plaats')

  favorite = tables.TemplateColumn('<i class="fa fa-star-o"></i>', verbose_name=" ")

  class Meta:
    model = Profile
    # add class="paleblue" to <table> tag
    attrs = {"class": "table table-hover table-striped table-bordered"}
    sequence = ('first_name', 'last_name', 'street_zip', 'city', 'phone', 'email', 'birthday')