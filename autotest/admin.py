from django.contrib import admin

# Register your models here.

from autotest.models import SuiteCount


class SuiteCountAdmin(admin.ModelAdmin):
    list_display = ('group', 'suite', 'count')


admin.site.register(SuiteCount, SuiteCountAdmin)

