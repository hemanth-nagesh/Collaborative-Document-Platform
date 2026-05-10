from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import Comment
from .serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer

	def get_object(self):
		try:
			return super().get_object()
		except Http404:
			raise NotFound(detail='Comment not found.')

	def get_queryset(self):
		queryset = super().get_queryset().select_related(
			'author',
			'document',
			'parent',
		).prefetch_related('replies')

		if self.action == 'list':
			document_id = self.request.query_params.get('document')
			if document_id:
				queryset = queryset.filter(document_id=document_id, parent__isnull=True)
			else:
				queryset = queryset.none()

		return queryset

	def list(self, request, *args, **kwargs):
		if not request.query_params.get('document'):
			return Response(
				{'error': 'document query param is required.'},
				status=status.HTTP_400_BAD_REQUEST,
			)
		return super().list(request, *args, **kwargs)
