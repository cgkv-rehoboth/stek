from django.db import models

# Import models of base app
from base.models import *

class Slide(models.Model):
  image       = models.ImageField("Afbeelding", upload_to='slides')
  title       = models.CharField("Titel", max_length=255)
  description = models.TextField("Beschrijving", blank=True, null=True)
  order       = models.IntegerField("Volgorde")
  showtext    = models.BooleanField("Tekst weergeven", default=False)
  live        = models.BooleanField(default=True)
  owner       = models.ForeignKey(Profile, verbose_name="Eigenaar")

  class Meta:
    ordering = ('order',)

  def __str__(self): return self.title

  def save(self, *args, **kwargs):
    # Save before ordering the rest
    super().save(*args, **kwargs)

    # Check if order already exists
    nextslide = Slide.objects.filter(order=self.order).exclude(pk=self.pk).first()
    if nextslide:
      # Shift all the other slides one order down
      nextslide.order += 1
      nextslide.save()


  def delete(self, *args, **kwargs):
    print("CUstom deletion")
    order = self.order

    # Delete the image from the server
    self.image.delete()

    # Delete before ordering the rest
    super().delete(*args, **kwargs)

    # Shift next slides one order up
    for slide in Slide.objects.filter(order__gt=order):
      slide.order -= 1
      slide.save()

  def move(self, move):
    """Change the ordering of the object."""
    if move == 'UP' and not self.order is 1:
      try:
        # Get previous
        mm = Slide.objects.filter(order__lt=self.order).order_by('-order')[0]

        # Set order for itself
        self.order = mm.order
        self.save()

        # Set order for the previous  # Not needed anymore, because of the automatic ordering in save()
        #mm.order += 1
        #mm.save()
        print("Save move")
      except IndexError:
        pass
    elif move == 'DOWN':
      try:
        mm = Slide.objects.filter(order__gt=self.order).order_by('order')[0]

        # Set order for next previous
        mm.order = self.order
        mm.save()

        # Set order for itself  # Not needed anymore, because of the automatic ordering in save()
        #self.order = mm.order
        #self.save()
      except IndexError:
        pass
