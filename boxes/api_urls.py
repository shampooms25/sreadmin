"""URL patterns for the boxes API."""

from django.urls import path

from .api_views import (
    box_detail,
    boxes_bulk_update,
    boxes_collection,
    gps_models_list,
    hardware_models_list,
)

app_name = "boxes_api"

urlpatterns = [
    path("", boxes_collection, name="boxes_collection"),
    path("bulk-update/", boxes_bulk_update, name="boxes_bulk_update"),
    path("hardware-models/", hardware_models_list, name="hardware_models"),
    path("gps-models/", gps_models_list, name="gps_models"),
    path("<int:box_id>/", box_detail, name="box_detail"),
]
