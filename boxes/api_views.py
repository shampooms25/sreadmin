"""REST-style API views for managing boxes via appliance tokens."""

import json
import logging
from typing import Any, Dict, Optional

from django.db import IntegrityError, transaction
from django.db.models import Q, QuerySet
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from captive_portal.api_views import appliance_auth_required

from .models import Box, GPSModel, HardwareModel

logger = logging.getLogger(__name__)


def _json_error(message: str, *, status: int = 400, extra: Optional[Dict[str, Any]] = None) -> JsonResponse:
    payload = {"success": False, "message": message, "timestamp": timezone.now().isoformat()}
    if extra:
        payload.update(extra)
    return JsonResponse(payload, status=status)


def _load_json_body(request) -> Dict[str, Any]:
    try:
        body = request.body.decode("utf-8") or "{}"
        return json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"JSON inválido: {exc}") from exc


def _serialize_hardware(model: Optional[HardwareModel]) -> Optional[Dict[str, Any]]:
    if not model:
        return None
    return {
        "id": model.id,
        "nome": model.nome,
        "fabricante": model.fabricante,
        "cpu": model.cpu,
        "arquitetura": model.arquitetura,
    }


def _serialize_gps(model: Optional[GPSModel]) -> Optional[Dict[str, Any]]:
    if not model:
        return None
    return {
        "id": model.id,
        "nome": model.nome,
        "fabricante": model.fabricante,
        "tecnologia": model.tecnologia,
    }


def _serialize_box(box: Box) -> Dict[str, Any]:
    return {
        "id": box.id,
        "nome": box.nome,
        "ativo": box.ativo,
        "hostname": box.hostname,
        "hardware_model_id": box.hardware_model_id,
        "gps_model_id": box.gps_model_id,
        "hardware_model": _serialize_hardware(box.hardware_model),
        "gps_model": _serialize_gps(box.gps_model),
        "chave_api_wireguard": box.chave_api_wireguard,
        "chave_api_opnsense": box.chave_api_opnsense,
        "created_at": box.created_at.isoformat() if box.created_at else None,
        "updated_at": box.updated_at.isoformat() if box.updated_at else None,
    }


def _apply_box_filters(qs: QuerySet[Box], request) -> QuerySet[Box]:
    hostname = request.GET.get("hostname")
    if hostname:
        qs = qs.filter(hostname__iexact=hostname.strip())

    ativo = request.GET.get("ativo")
    if ativo is not None:
        if ativo.lower() in {"true", "1"}:
            qs = qs.filter(ativo=True)
        elif ativo.lower() in {"false", "0"}:
            qs = qs.filter(ativo=False)

    hardware_model = request.GET.get("hardware_model")
    if hardware_model:
        qs = qs.filter(hardware_model_id=hardware_model)

    gps_model = request.GET.get("gps_model")
    if gps_model:
        qs = qs.filter(gps_model_id=gps_model)

    search = request.GET.get("search")
    if search:
        qs = qs.filter(Q(nome__icontains=search) | Q(hostname__icontains=search))

    ids = request.GET.get("ids")
    if ids:
        cleaned_ids = [pk for pk in ids.split(",") if pk.strip().isdigit()]
        if cleaned_ids:
            qs = qs.filter(id__in=cleaned_ids)

    return qs


def _assign_relations(box: Box, data: Dict[str, Any]) -> None:
    if "hardware_model_id" in data:
        hardware_id = data.get("hardware_model_id")
        if hardware_id in (None, "", 0):
            box.hardware_model = None
        else:
            box.hardware_model = get_object_or_404(HardwareModel, pk=hardware_id)

    if "gps_model_id" in data:
        gps_id = data.get("gps_model_id")
        if gps_id in (None, "", 0):
            box.gps_model = None
        else:
            box.gps_model = get_object_or_404(GPSModel, pk=gps_id)


def _update_box_fields(box: Box, payload: Dict[str, Any]) -> None:
    if "nome" in payload:
        nome = (payload.get("nome") or "").strip()
        if not nome:
            raise ValueError("O campo 'nome' não pode ser vazio.")
        box.nome = nome

    if "hostname" in payload:
        hostname = (payload.get("hostname") or "").strip()
        if not hostname:
            raise ValueError("O campo 'hostname' não pode ser vazio.")
        box.hostname = hostname

    if "ativo" in payload:
        box.ativo = bool(payload.get("ativo"))

    for field in ("chave_api_wireguard", "chave_api_opnsense"):
        if field in payload:
            setattr(box, field, (payload.get(field) or "").strip())


@csrf_exempt
@require_http_methods(["GET", "POST"])
@appliance_auth_required
def boxes_collection(request):
    """List or create boxes for appliance scripts."""

    if request.method == "GET":
        qs = _apply_box_filters(Box.objects.all(), request)
        total = qs.count()

        try:
            limit = int(request.GET.get("limit", 100))
        except ValueError:
            limit = 100
        limit = max(1, min(limit, 500))

        try:
            offset = int(request.GET.get("offset", 0))
        except ValueError:
            offset = 0
        offset = max(0, offset)

        sliced = qs[offset : offset + limit]
        results = [_serialize_box(box) for box in sliced]
        return JsonResponse(
            {
                "success": True,
                "results": results,
                "metadata": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                },
            }
        )

    # POST
    try:
        payload = _load_json_body(request)
    except ValueError as exc:
        return _json_error(str(exc))

    nome = (payload.get("nome") or "").strip()
    hostname = (payload.get("hostname") or "").strip()

    if not nome or not hostname:
        return _json_error("Campos 'nome' e 'hostname' são obrigatórios.")

    box = Box(
        nome=nome,
        hostname=hostname,
        ativo=payload.get("ativo", True),
        chave_api_wireguard=payload.get("chave_api_wireguard", "").strip(),
        chave_api_opnsense=payload.get("chave_api_opnsense", "").strip(),
    )

    try:
        _assign_relations(box, payload)
    except Exception as exc:
        return _json_error(str(exc))

    try:
        with transaction.atomic():
            box.save()
    except IntegrityError as exc:
        logger.warning("Erro ao criar box: %s", exc)
        return _json_error("Não foi possível criar o box (hostname duplicado?).")

    return JsonResponse({"success": True, "result": _serialize_box(box)}, status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
@appliance_auth_required
def box_detail(request, box_id: int):
    """Retrieve, update or delete a single box."""

    box = get_object_or_404(Box, pk=box_id)

    if request.method == "GET":
        return JsonResponse({"success": True, "result": _serialize_box(box)})

    if request.method == "DELETE":
        box.delete()
        return JsonResponse({"success": True, "message": "Box removido."}, status=204)

    try:
        payload = _load_json_body(request)
    except ValueError as exc:
        return _json_error(str(exc))

    try:
        _update_box_fields(box, payload)
    except ValueError as exc:
        return _json_error(str(exc))

    try:
        _assign_relations(box, payload)
    except Exception as exc:
        return _json_error(str(exc))

    try:
        with transaction.atomic():
            box.save()
    except IntegrityError as exc:
        logger.warning("Erro ao atualizar box: %s", exc)
        return _json_error("Não foi possível atualizar o box (hostname duplicado?).")

    return JsonResponse({"success": True, "result": _serialize_box(box)})


@csrf_exempt
@require_http_methods(["POST"])
@appliance_auth_required
def boxes_bulk_update(request):
    """Apply partial updates to multiple boxes in a single call."""

    try:
        payload = _load_json_body(request)
    except ValueError as exc:
        return _json_error(str(exc))

    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return _json_error("Envie uma lista 'items' com ao menos um objeto para atualizar.")

    stop_on_error = bool(payload.get("stop_on_error", False))
    results = []
    errors = []

    for entry in items:
        box_id = entry.get("id")
        data = entry.get("data", {})

        if not box_id:
            errors.append({"id": box_id, "message": "ID do box é obrigatório."})
            if stop_on_error:
                break
            continue

        try:
            box = Box.objects.get(pk=box_id)
        except Box.DoesNotExist:
            errors.append({"id": box_id, "message": "Box não encontrado."})
            if stop_on_error:
                break
            continue

        try:
            _update_box_fields(box, data)
            _assign_relations(box, data)
            with transaction.atomic():
                box.save()
            results.append(_serialize_box(box))
        except ValueError as exc:
            errors.append({"id": box_id, "message": str(exc)})
            if stop_on_error:
                break
        except Exception as exc:  # pragma: no cover - defensive log
            logger.exception("Erro inesperado no bulk update para box %s", box_id)
            errors.append({"id": box_id, "message": str(exc)})
            if stop_on_error:
                break

    status_code = 200 if not errors else 207  # 207 Multi-Status indica sucesso parcial
    return JsonResponse(
        {
            "success": not errors,
            "updated": results,
            "errors": errors,
            "metadata": {
                "requested": len(items),
                "updated": len(results),
                "errors": len(errors),
                "stop_on_error": stop_on_error,
            },
        },
        status=status_code,
    )


@csrf_exempt
@require_http_methods(["GET"])
@appliance_auth_required
def hardware_models_list(request):
    """Return lightweight metadata about hardware models."""

    qs = HardwareModel.objects.all().order_by("nome")
    results = [
        {
            "id": model.id,
            "nome": model.nome,
            "fabricante": model.fabricante,
            "cpu": model.cpu,
            "memoria_max_gb": model.memoria_max_gb,
        }
        for model in qs
    ]
    return JsonResponse({"success": True, "results": results, "total": len(results)})


@csrf_exempt
@require_http_methods(["GET"])
@appliance_auth_required
def gps_models_list(request):
    """Return lightweight metadata about GPS models."""

    qs = GPSModel.objects.all().order_by("nome")
    results = [
        {
            "id": model.id,
            "nome": model.nome,
            "fabricante": model.fabricante,
            "tecnologia": model.tecnologia,
        }
        for model in qs
    ]
    return JsonResponse({"success": True, "results": results, "total": len(results)})
