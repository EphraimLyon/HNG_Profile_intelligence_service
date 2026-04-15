from rest_framework import serializers
from .models import Profile

class ProfileCreateSerializer(serializers.Serializer):
    name = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "gender", "age", "age_group", "country_id"]