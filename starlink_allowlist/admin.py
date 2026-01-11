from django.contrib import admin
from django.db.models import Count, Q

from .models import CustomPrefix, StarlinkASN, StarlinkPrefix, StarlinkUpdateRun


@admin.register(StarlinkASN)
class StarlinkASNAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'enabled', 'americas_only', 'active_prefixes', 'updated_at')
    list_filter = ('enabled', 'americas_only')
    search_fields = ('number', 'name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_active_prefixes=Count('prefixes', filter=Q(prefixes__active=True)))

    @admin.display(description='Active prefixes', ordering='_active_prefixes')
    def active_prefixes(self, obj):
        return getattr(obj, '_active_prefixes', 0)


@admin.register(StarlinkPrefix)
class StarlinkPrefixAdmin(admin.ModelAdmin):
    list_display = ('cidr', 'ip_version', 'asn', 'region', 'country', 'rir', 'is_americas', 'active', 'last_seen_at')
    list_filter = ('ip_version', 'asn', 'region', 'rir', 'country', 'is_americas', 'active')
    search_fields = ('cidr', 'country', 'rir')


@admin.register(StarlinkUpdateRun)
class StarlinkUpdateRunAdmin(admin.ModelAdmin):
    list_display = ('started_at', 'finished_at', 'status', 'source', 'total_prefixes', 'added_prefixes', 'removed_prefixes')
    list_filter = ('status', 'source')
    readonly_fields = ('started_at', 'finished_at', 'details')


@admin.register(CustomPrefix)
class CustomPrefixAdmin(admin.ModelAdmin):
    list_display = ('cidr', 'ip_version', 'name', 'region', 'country', 'enabled', 'updated_at')
    list_filter = ('ip_version', 'enabled', 'region', 'country')
    search_fields = ('cidr', 'name', 'country', 'region')
