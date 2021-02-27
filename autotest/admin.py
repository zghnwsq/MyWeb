from django.contrib import admin

# Register your models here.

from autotest.models import SuiteCount, Node, RegisterFunction


class SuiteCountAdmin(admin.ModelAdmin):
    list_display = ('group', 'suite', 'count')


class NodeAdmin(admin.ModelAdmin):
    list_display = ('ip_port', 'tag', 'status')


class RegisterFunctionAdmin(admin.ModelAdmin):
    list_display = ('group', 'suite', 'func', 'node')


admin.site.register(SuiteCount, SuiteCountAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(RegisterFunction, RegisterFunctionAdmin)


