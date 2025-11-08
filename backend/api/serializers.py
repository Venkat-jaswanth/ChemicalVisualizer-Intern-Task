from rest_framework import serializers
from .models import Dataset


class DatasetSerializer(serializers.ModelSerializer):
    """
    Serializer for the Dataset model.
    It will translate our Dataset object to and from JSON.
    """

    class Meta:
        model = Dataset

        fields = ["id", "file", "summary", "uploaded_at", "name"]
        read_only_fields = ["id", "summary", "uploaded_at"]
