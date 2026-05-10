from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'document',
            'author',
            'parent',
            'content',
            'created_at',
            'updated_at',
            'children',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'children']

    def get_children(self, obj):
        replies = obj.replies.all()
        if not replies:
            return []
        serializer = CommentSerializer(replies, many=True, context=self.context)
        return serializer.data

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Content cannot be blank.')
        return value

    def validate(self, attrs):
        document = attrs.get('document') or getattr(self.instance, 'document', None)
        parent = attrs.get('parent')

        if parent and document and parent.document_id != document.id:
            raise serializers.ValidationError({'parent': 'Parent must belong to the same document.'})

        if parent and self.instance and parent.id == self.instance.id:
            raise serializers.ValidationError({'parent': 'A comment cannot be its own parent.'})

        return attrs
