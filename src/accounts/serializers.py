from rest_framework import serializers
from django.contrib.auth.models import User

from accounts.models import Company


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["industry"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['industry'],
            'text': representation['industry']
        }


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["city"]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['city'],
            'text': representation['city']
        }


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["state"]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['state'],
            'text': representation['state']
        }


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["country"]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['country'],
            'text': representation['country']
        }


class YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["year_founded"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['year_founded'],
            'text': representation['year_founded']
        }