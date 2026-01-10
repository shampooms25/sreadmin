from __future__ import annotations

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from captive_portal.api_views import appliance_auth_required

from .models import StarlinkPrefix


@csrf_exempt
@require_http_methods(["GET"])
@appliance_auth_required
def prefixes(request):
    """Lista de prefixes Starlink para consumo por scripts.

    GET /api/starlink/prefixes/?format=json|text&ip_version=4|6&include_non_americas=1
    """
    output_format = (request.GET.get('format') or 'json').strip().lower()

    ip_version_raw = (request.GET.get('ip_version') or '').strip()
    include_non_americas = (request.GET.get('include_non_americas') or '').strip() in {'1', 'true', 'yes'}

    qs = StarlinkPrefix.objects.filter(active=True)

    if ip_version_raw in {'4', '6'}:
        qs = qs.filter(ip_version=int(ip_version_raw))

    if not include_non_americas:
        qs = qs.filter(is_americas=True)

    cidrs = list(qs.values_list('cidr', flat=True))

    if output_format == 'text':
        body = '\n'.join(cidrs) + ('\n' if cidrs else '')
        return HttpResponse(body, content_type='text/plain; charset=utf-8')

    return JsonResponse(
        {
            'count': len(cidrs),
            'prefixes': cidrs,
        }
    )


@csrf_exempt
@require_http_methods(["GET"])
@appliance_auth_required
def health(request):
    return JsonResponse({'status': 'ok'})
