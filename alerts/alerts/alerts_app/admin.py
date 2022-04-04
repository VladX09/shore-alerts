from django.contrib import admin

from . import models


admin.site.register(models.Alert)
admin.site.register(models.AlertItem)
