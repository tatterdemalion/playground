from django.db import models
from tenant_schemas.models import TenantMixin


class Library(TenantMixin):
    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
