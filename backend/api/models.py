# backend/api/models.py

from django.db import models


class Dataset(models.Model):
    """
    Model to store the last 5 uploaded datasets, their summary,
    and a reference to the file.
    """

    file = models.FileField(upload_to="uploads/")

    summary = models.JSONField(null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Dataset: {self.name} (Uploaded on {self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        ordering = ["-uploaded_at"]
