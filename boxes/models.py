from django.db import models


class HardwareModel(models.Model):
	nome = models.CharField(max_length=255)
	fabricante = models.CharField(max_length=255, blank=True)
	cpu = models.CharField(max_length=255, blank=True)
	arquitetura = models.CharField(max_length=100, blank=True)
	memoria_max_gb = models.PositiveIntegerField(null=True, blank=True)
	armazenamento = models.CharField(max_length=255, blank=True)
	portas_lan = models.PositiveIntegerField(null=True, blank=True)
	wifi = models.BooleanField(default=False)
	observacoes = models.TextField(blank=True)

	class Meta:
		verbose_name = "Modelo de Hardware"
		verbose_name_plural = "Modelos de Hardware"

	def __str__(self) -> str:
		return f"{self.nome} ({self.fabricante})" if self.fabricante else self.nome


class GPSModel(models.Model):
	nome = models.CharField(max_length=255)
	fabricante = models.CharField(max_length=255, blank=True)
	tecnologia = models.CharField(max_length=255, blank=True)
	interface_conexao = models.CharField(max_length=255, blank=True)
	protocolo = models.CharField(max_length=255, blank=True)
	taxa_atualizacao_hz = models.PositiveIntegerField(null=True, blank=True)
	antena_externa = models.BooleanField(default=False)
	observacoes = models.TextField(blank=True)

	class Meta:
		verbose_name = "Modelo de GPS"
		verbose_name_plural = "Modelos de GPS"

	def __str__(self) -> str:
		return f"{self.nome} ({self.fabricante})" if self.fabricante else self.nome


class Box(models.Model):
	nome = models.CharField(max_length=255)
	ativo = models.BooleanField(default=True)
	hostname = models.CharField(max_length=255, unique=True)
	hardware_model = models.ForeignKey(
		HardwareModel,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="boxes",
	)
	gps_model = models.ForeignKey(
		GPSModel,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="boxes",
	)
	chave_api_wireguard = models.CharField(max_length=255, blank=True)
	chave_api_opnsense = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Box"
		verbose_name_plural = "Boxes"
		ordering = ["-id"]

	def __str__(self) -> str:
		return self.nome
