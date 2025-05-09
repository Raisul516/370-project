from django.contrib import admin
from .models import Historicalevents

class HistoricalEventsAdmin(admin.ModelAdmin):
    list_display = ('title', 'eventdate', 'category', 'location', 'importance')

admin.site.register(Historicalevents, HistoricalEventsAdmin)