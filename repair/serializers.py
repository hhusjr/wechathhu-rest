from rest_framework import serializers
from repair.models import FaultCategory, NotificationUser, RepairRequest

class FaultCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FaultCategory
        fields = (
            'id',
            'name'
        )

class RepairRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairRequest
        fields = (
            'user',
            'location',
            'category',
            'description'
        )
        read_only_fields = ('user', )

class RepairRequestViewSerializer(RepairRequestSerializer):
    category = FaultCategorySerializer(read_only=True)

    class Meta(RepairRequestSerializer.Meta):
        fields = RepairRequestSerializer.Meta.fields + ('id', 'status', 'created')