from django.contrib import admin

# Register your models here.
from newsmim import models
admin.site.register(models.Article)
admin.site.register(models.SMIMCategory)
admin.site.register(models.Fltobj)
admin.site.register(models.Fltdata)