# moments/models.py
from django.db import models

class Moment(models.Model):
    image = models.ImageField(upload_to="moments/")
    caption = models.CharField(max_length=255, blank=True)  # small caption
    link = models.URLField(blank=True, null=True, help_text="Permalink to Instagram or external page")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.caption or f"Moment {self.id}"
