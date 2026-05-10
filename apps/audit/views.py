from django.http import Http404
from django.utils.dateparse import parse_date
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = AuditLog.objects.select_related('actor').all()
	serializer_class = AuditLogSerializer

	def get_object(self):
		try:
			return super().get_object()
		except Http404:
			raise NotFound(detail='Audit log not found.')

	def get_queryset(self):
		queryset = super().get_queryset()
		actor_id = self.request.query_params.get('actor')
		date_from = self.request.query_params.get('date_from')
		date_to = self.request.query_params.get('date_to')

		if actor_id:
			queryset = queryset.filter(actor_id=actor_id)

		if date_from:
			queryset = queryset.filter(timestamp__date__gte=parse_date(date_from))

		if date_to:
			queryset = queryset.filter(timestamp__date__lte=parse_date(date_to))

		return queryset

	def list(self, request, *args, **kwargs):
		date_from = request.query_params.get('date_from')
		date_to = request.query_params.get('date_to')

		if date_from and not parse_date(date_from):
			return Response(
				{'error': 'date_from must be YYYY-MM-DD.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		if date_to and not parse_date(date_to):
			return Response(
				{'error': 'date_to must be YYYY-MM-DD.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		return super().list(request, *args, **kwargs)
