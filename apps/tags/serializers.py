from rest_framework import serializers

from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Tag name cannot be blank.')
        if Tag.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError('Tag with this name already exists.')
        return value
