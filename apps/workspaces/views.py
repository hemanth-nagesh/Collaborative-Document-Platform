from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from django.db.models import Count

from apps.workspaces.serializers import WorkspaceSerializer, WorkspaceMemberSerializer
from .models import Workspace, WorkspaceMember, WorkspaceRole

class WorkspaceViewSet(viewsets.ModelViewSet):
    queryset = Workspace.objects.select_related('owner').all()
    serializer_class = WorkspaceSerializer

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail='Workspace not found.')

    # 1.5 POST /api/workspaces/ – atomic: create + add owner as admin
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Save workspace
        workspace = serializer.save()
        # Add owner automatically as admin
        WorkspaceMember.objects.create(
            workspace=workspace,
            user=workspace.owner,
            role=WorkspaceRole.ADMIN
        )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 1.6 GET /api/workspaces/{id}/ – annotate member count
    def retrieve(self, request, *args, **kwargs):
        # Override retrieve to annotate member count safely
        workspace = (
            Workspace.objects.select_related('owner')
            .annotate(member_count=Count('members'))
            .filter(pk=kwargs.get('pk'))
            .first()
        )
        if not workspace:
            return Response({'error': 'Workspace not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(workspace)
        data = serializer.data
        data['member_count'] = workspace.member_count
        return Response(data)

    # 1.7 POST /api/workspaces/{id}/members/ – add member with role
    @action(detail=True, methods=['post'])
    def members(self, request, pk=None):
        workspace = self.get_object()
        user_id = request.data.get('user')
        role = request.data.get('role', WorkspaceRole.VIEWER)
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            member = WorkspaceMember.objects.create(
                workspace=workspace,
                user_id=user_id,
                role=role
            )
            serializer = WorkspaceMemberSerializer(member)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError: # Catches UniqueConstraint mapping in models
            return Response({"error": "User is already a member of this workspace."}, status=status.HTTP_409_CONFLICT)

    # 1.8 GET /api/workspaces/{id}/members_list/ – list with roles
    # (Notice REST pattern: GET to /members/ mapped using the same action, so we rename it)
    @members.mapping.get
    def list_members(self, request, pk=None):
        workspace = self.get_object()
        members = WorkspaceMember.objects.filter(workspace=workspace).select_related('user')
        serializer = WorkspaceMemberSerializer(members, many=True)
        return Response(serializer.data)

    # 1.9 GET /api/workspaces/{id}/summary/ – doc + member + comment count
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        workspace = Workspace.objects.filter(pk=pk).annotate(
            member_count=Count('members', distinct=True),
            document_count=Count('documents', distinct=True),
            comment_count=Count('documents__comments', distinct=True),
        ).first()

        if not workspace:
            return Response({'error': 'Workspace not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "workspace_id": workspace.id,
            "name": workspace.name,
            "member_count": workspace.member_count,
            "document_count": workspace.document_count,
            "comment_count": workspace.comment_count,
        })