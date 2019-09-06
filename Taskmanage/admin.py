from django.contrib import admin

# Register your models here.
from Taskmanage import models

admin.site.register(models.Taskitem)
admin.site.register(models.Taskfeedbacks)

