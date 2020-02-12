from guide.models import Guide, GuideCategory
from rest_framework import serializers

class GuideCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideCategory
        fields = (
            'id',
            'name'
        )

class GuideSerializer(serializers.ModelSerializer):
    category = GuideCategorySerializer(read_only=True)
    class Meta:
        model = Guide
        fields = (
            'id',
            'name',
            'category',
            'created'
        )
