from __future__ import annotations

from django.db import models
from django.utils import timezone


class StarlinkASN(models.Model):
    number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=200, blank=True)
    enabled = models.BooleanField(default=True)
    americas_only = models.BooleanField(
        default=True,
        help_text='Se true, a API padrão expõe apenas prefixes classificados como Américas.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Starlink ASN'
        verbose_name_plural = 'Starlink ASNs'
        ordering = ['number']

    def __str__(self) -> str:
        return f'AS{self.number}' + (f' - {self.name}' if self.name else '')


class StarlinkPrefix(models.Model):
    IPV4 = 4
    IPV6 = 6
    IP_VERSION_CHOICES = (
        (IPV4, 'IPv4'),
        (IPV6, 'IPv6'),
    )

    cidr = models.CharField(max_length=43, unique=True)
    ip_version = models.PositiveSmallIntegerField(choices=IP_VERSION_CHOICES)
    asn = models.ForeignKey(StarlinkASN, on_delete=models.PROTECT, related_name='prefixes')

    rir = models.CharField(max_length=20, blank=True, help_text='Ex: arin, lacnic, ripe, apnic, afrinic, nicbr')
    country = models.CharField(max_length=2, blank=True, help_text='ISO-3166 alpha-2 quando disponível')
    is_americas = models.BooleanField(default=True)

    first_seen_at = models.DateTimeField(default=timezone.now)
    last_seen_at = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Starlink Prefix'
        verbose_name_plural = 'Starlink Prefixes'
        ordering = ['ip_version', 'cidr']

    def __str__(self) -> str:
        return self.cidr


class StarlinkUpdateRun(models.Model):
    STATUS_SUCCESS = 'success'
    STATUS_ERROR = 'error'
    STATUS_CHOICES = (
        (STATUS_SUCCESS, 'Success'),
        (STATUS_ERROR, 'Error'),
    )

    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUCCESS)

    source = models.CharField(max_length=50, default='bgpview')
    asns = models.JSONField(default=list, blank=True)

    total_prefixes = models.PositiveIntegerField(default=0)
    added_prefixes = models.PositiveIntegerField(default=0)
    removed_prefixes = models.PositiveIntegerField(default=0)

    error = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Starlink Update Run'
        verbose_name_plural = 'Starlink Update Runs'
        ordering = ['-started_at']

    def __str__(self) -> str:
        return f'{self.started_at:%Y-%m-%d %H:%M} ({self.status})'
