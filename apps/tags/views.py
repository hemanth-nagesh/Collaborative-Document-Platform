from django.db import IntegrityError
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import Tag
from .serializers import TagSerializer


class TagViewSet(viewsets.ModelViewSet):
	queryset = Tag.objects.all()
	serializer_class = TagSerializer

	def get_object(self):
		try:
			return super().get_object()
		except Http404:
			raise NotFound(detail='Tag not found.')

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		try:
			self.perform_create(serializer)
		except IntegrityError:
			return Response(
				{'error': 'Tag with this name already exists.'},
				status=status.HTTP_400_BAD_REQUEST,
			)
		return Response(serializer.data, status=status.HTTP_201_CREATED)
