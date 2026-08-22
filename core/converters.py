from django.urls import register_converter
from django.urls.converters import UUIDConverter

register_converter(UUIDConverter, "account-uuid")
register_converter(UUIDConverter, "transaction-uuid")
