from django.contrib import admin

from .models import Box, GPSModel, HardwareModel


@admin.register(HardwareModel)
class HardwareModelAdmin(admin.ModelAdmin):
	list_display = ("nome", "fabricante", "cpu", "portas_lan", "wifi")
	search_fields = ("nome", "fabricante", "cpu", "arquitetura")


@admin.register(GPSModel)
class GPSModelAdmin(admin.ModelAdmin):
	list_display = ("nome", "fabricante", "tecnologia", "interface_conexao", "antena_externa")
	search_fields = ("nome", "fabricante", "tecnologia", "interface_conexao")


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"nome",
		"ativo",
		"hostname",
		"hardware_model",
		"gps_model",
		"created_at",
	)
	list_filter = ("ativo", "hardware_model", "gps_model")
	search_fields = ("nome", "hostname", "chave_api_wireguard", "chave_api_opnsense")
