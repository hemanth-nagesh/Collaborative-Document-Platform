from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from apps.audit.models import AuditLog

from .models import Document, DocumentVersion
from .serializers import (
    DocumentSerializer,
    DocumentTagActionSerializer,
    DocumentVersionSerializer,
)


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    queryset = Document.objects.select_related('workspace', 'created_by').prefetch_related('tags')

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail='Document not found.')

    def get_queryset(self):
        queryset = (
            Document.objects.select_related('workspace', 'created_by')
            .prefetch_related('tags')
            .annotate(version_count=Count('versions', distinct=True))
        )

        workspace_id = self.request.query_params.get('workspace')
        workspace_ids = self.request.query_params.get('workspace__in')
        status_value = self.request.query_params.get('status')
        status_in = self.request.query_params.get('status__in')
        query = self.request.query_params.get('q')
        updated_after = self.request.query_params.get('updated_at__gte')
        updated_before = self.request.query_params.get('updated_at__lte')
        tag_name = self.request.query_params.get('tag')

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        if workspace_ids:
            queryset = queryset.filter(workspace_id__in=[w.strip() for w in workspace_ids.split(',') if w.strip()])
        if status_value:
            queryset = queryset.filter(status=status_value)
        if status_in:
            queryset = queryset.filter(status__in=[s.strip() for s in status_in.split(',') if s.strip()])
        if updated_after:
            queryset = queryset.filter(updated_at__gte=updated_after)
        if updated_before:
            queryset = queryset.filter(updated_at__lte=updated_before)
        if tag_name:
            queryset = queryset.filter(tags__name__iexact=tag_name)
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))

        return queryset.distinct()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()

        version_number = document.versions.count() + 1
        DocumentVersion.objects.create(
            document=document,
            content=document.content,
            version_number=version_number,
            saved_by=document.created_by,
        )

        output = self.get_serializer(document)
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()

        version_number = document.versions.count() + 1
        DocumentVersion.objects.create(
            document=document,
            content=document.content,
            version_number=version_number,
            saved_by=document.created_by,
        )

        return Response(self.get_serializer(document).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        document = self.get_object()
        versions = (
            DocumentVersion.objects.filter(document=document)
            .select_related('document', 'saved_by')
            .order_by('version_number')
        )
        serializer = DocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        document = self.get_object()
        version_stats = DocumentVersion.objects.filter(document=document).aggregate(
            version_count=Count('id'),
            contributor_count=Count('saved_by', distinct=True),
        )
        comment_count = 0
        if hasattr(document, 'comments'):
            comment_count = document.comments.count()

        return Response(
            {
                'document_id': str(document.id),
                'version_count': version_stats['version_count'],
                'comment_count': comment_count,
                'contributor_count': version_stats['contributor_count'] or 0,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def tags(self, request, pk=None):
        document = self.get_object()
        serializer = DocumentTagActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tag_ids = serializer.validated_data['tag_ids']
        current_tag_ids = set(document.tags.values_list('id', flat=True))
        new_tag_ids = [tag_id for tag_id in tag_ids if tag_id not in current_tag_ids]

        if new_tag_ids:
            document.tags.add(*new_tag_ids)

        AuditLog.objects.create(
            actor=document.created_by,
            action='tags_added',
            model_name='Document',
            object_id=str(document.id),
        )

        output = self.get_serializer(document)
        return Response(
            {
                'message': 'Tags added successfully.',
                'added_count': len(new_tag_ids),
                'document': output.data,
            },
            status=status.HTTP_200_OK,
        )
