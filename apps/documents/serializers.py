from rest_framework import serializers

from apps.tags.models import Tag

from .models import Document, DocumentVersion


class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = [
            'id',
            'document',
            'content',
            'version_number',
            'saved_by',
            'saved_at',
        ]
        read_only_fields = ['id', 'saved_at']


class DocumentSerializer(serializers.ModelSerializer):
    version_count = serializers.SerializerMethodField()
    tag_names = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'content',
            'workspace',
            'created_by',
            'status',
            'tags',
            'tag_names',
            'version_count',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at', 'version_count', 'tag_names']

    def get_version_count(self, obj):
        return getattr(obj, 'version_count', obj.versions.count())

    def get_tag_names(self, obj):
        return list(obj.tags.values_list('name', flat=True))

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError('Title must be at least 3 characters long.')
        return value

    def validate(self, attrs):
        content = attrs.get('content')
        if content is not None and not content.strip():
            raise serializers.ValidationError({'content': 'Document content cannot be empty.'})
        return attrs


class DocumentTagActionSerializer(serializers.Serializer):
    tag_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        help_text='List of tag UUIDs to add to this document.',
    )

    def validate_tag_ids(self, value):
        unique_ids = list(dict.fromkeys(value))
        existing_ids = set(Tag.objects.filter(id__in=unique_ids).values_list('id', flat=True))
        missing_ids = [str(tag_id) for tag_id in unique_ids if tag_id not in existing_ids]
        if missing_ids:
            raise serializers.ValidationError(f'Tag(s) not found: {", ".join(missing_ids)}')
        return unique_ids
