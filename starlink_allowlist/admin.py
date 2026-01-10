from django.contrib import admin

from .models import StarlinkASN, StarlinkPrefix, StarlinkUpdateRun


@admin.register(StarlinkASN)
class StarlinkASNAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'enabled', 'americas_only', 'updated_at')
    list_filter = ('enabled', 'americas_only')
    search_fields = ('number', 'name')


@admin.register(StarlinkPrefix)
class StarlinkPrefixAdmin(admin.ModelAdmin):
    list_display = ('cidr', 'ip_version', 'asn', 'rir', 'country', 'is_americas', 'active', 'last_seen_at')
    list_filter = ('ip_version', 'asn', 'rir', 'country', 'is_americas', 'active')
    search_fields = ('cidr',)


@admin.register(StarlinkUpdateRun)
class StarlinkUpdateRunAdmin(admin.ModelAdmin):
    list_display = ('started_at', 'finished_at', 'status', 'source', 'total_prefixes', 'added_prefixes', 'removed_prefixes')
    list_filter = ('status', 'source')
    readonly_fields = ('started_at', 'finished_at', 'details')
