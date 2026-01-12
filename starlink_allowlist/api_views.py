from __future__ import annotations

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from captive_portal.api_views import appliance_auth_required

from .models import CustomPrefix, StarlinkASN, StarlinkPrefix, StarlinkUpdateRun


@csrf_exempt
@require_http_methods(["GET"])
@appliance_auth_required
def prefixes(request):
    """Lista de prefixes Starlink para consumo por scripts.

    GET /api/starlink/prefixes/?format=json|text&ip_version=4|6&include_non_americas=1&include_custom=0|1
    """
    output_format = (request.GET.get('format') or 'json').strip().lower()

    ip_version_raw = (request.GET.get('ip_version') or '').strip()
    include_non_americas = (request.GET.get('include_non_americas') or '').strip() in {'1', 'true', 'yes'}
    include_custom = (request.GET.get('include_custom') or '').strip() in {'1', 'true', 'yes'}

    qs = StarlinkPrefix.objects.filter(active=True)

    if ip_version_raw in {'4', '6'}:
        qs = qs.filter(ip_version=int(ip_version_raw))

    if not include_non_americas:
        qs = qs.filter(is_americas=True)

    cidrs = list(qs.values_list('cidr', flat=True))

    if include_custom:
        cqs = CustomPrefix.objects.filter(enabled=True)
        if ip_version_raw in {'4', '6'}:
            cqs = cqs.filter(ip_version=int(ip_version_raw))
        cidrs += list(cqs.values_list('cidr', flat=True))

    # dedupe preserving order
    seen = set()
    unique_cidrs = []
    for c in cidrs:
        if c in seen:
            continue
        seen.add(c)
        unique_cidrs.append(c)
    cidrs = unique_cidrs

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
def prefixes_grouped(request):
    """Lista de prefixes agrupados por ASN (com metadados de localidade).

    GET /api/starlink/prefixes_grouped/?ip_version=4|6&include_non_americas=1&include_custom=0|1

    Retorna JSON com:
    - asns: [{ number, name, enabled, americas_only, prefixes: [...] }]
    - custom: [{ cidr, ip_version, name, region, country }]
    """
    ip_version_raw = (request.GET.get('ip_version') or '').strip()
    include_non_americas = (request.GET.get('include_non_americas') or '').strip() in {'1', 'true', 'yes'}
    include_custom = (request.GET.get('include_custom') or '').strip() in {'1', 'true', 'yes'}

    qs = StarlinkPrefix.objects.filter(active=True).select_related('asn')
    if ip_version_raw in {'4', '6'}:
        qs = qs.filter(ip_version=int(ip_version_raw))
    if not include_non_americas:
        qs = qs.filter(is_americas=True)

    asn_map: dict[int, dict] = {}
    for p in qs.order_by('asn__number', 'ip_version', 'cidr'):
        num = p.asn.number
        if num not in asn_map:
            asn_map[num] = {
                'number': p.asn.number,
                'name': p.asn.name,
                'enabled': p.asn.enabled,
                'americas_only': p.asn.americas_only,
                'count': 0,
                'prefixes': [],
            }
        asn_map[num]['count'] += 1
        asn_map[num]['prefixes'].append(
            {
                'cidr': p.cidr,
                'ip_version': p.ip_version,
                'region': p.region,
                'country': p.country,
                'rir': p.rir,
                'is_americas': p.is_americas,
            }
        )

    custom = []
    if include_custom:
        cqs = CustomPrefix.objects.filter(enabled=True)
        if ip_version_raw in {'4', '6'}:
            cqs = cqs.filter(ip_version=int(ip_version_raw))
        for c in cqs.order_by('ip_version', 'cidr'):
            custom.append(
                {
                    'cidr': c.cidr,
                    'ip_version': c.ip_version,
                    'name': c.name,
                    'region': c.region,
                    'country': c.country,
                }
            )

    return JsonResponse(
        {
            'count': sum(v['count'] for v in asn_map.values()) + len(custom),
            'asns': [asn_map[k] for k in sorted(asn_map.keys())],
            'custom': custom,
        }
    )


@csrf_exempt
@require_http_methods(["GET"])
@appliance_auth_required
def health(request):
    last_run = StarlinkUpdateRun.objects.order_by('-started_at').first()

    def dt(v):
        return v.isoformat() if v else None

    data = {
        'status': 'ok',
        'counts': {
            'starlink_prefixes_active_total': StarlinkPrefix.objects.filter(active=True).count(),
            'starlink_prefixes_active_americas': StarlinkPrefix.objects.filter(active=True, is_americas=True).count(),
            'custom_prefixes_enabled': CustomPrefix.objects.filter(enabled=True).count(),
        },
        'last_update_run': None,
    }

    if last_run:
        data['last_update_run'] = {
            'started_at': dt(last_run.started_at),
            'finished_at': dt(last_run.finished_at),
            'status': last_run.status,
            'source': last_run.source,
            'asns': last_run.asns,
            'total_prefixes': last_run.total_prefixes,
            'added_prefixes': last_run.added_prefixes,
            'removed_prefixes': last_run.removed_prefixes,
            'error': (last_run.error or '').strip() or None,
        }

    return JsonResponse(data)
