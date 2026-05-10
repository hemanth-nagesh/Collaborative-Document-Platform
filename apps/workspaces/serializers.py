from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Workspace, WorkspaceMember, role_choices

class WorkspaceSerializer(serializers.ModelSerializer):
    
    def validate_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Workspace name must be at least 3 characters long.")
        return value

    class Meta:
        model = Workspace
        fields = ['id', 'name', 'owner', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    # Ensure role falls within the valid choices explicitly, in case the model's models.Choices isn't correctly enforced
    role = serializers.ChoiceField(choices=role_choices)

    class Meta:
        model = WorkspaceMember
        fields = ['id', 'workspace', 'user', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']
        validators = [
            UniqueTogetherValidator(
                queryset=WorkspaceMember.objects.all(),
                fields=['workspace', 'user'],
                message="This user is already a member of this workspace."
            )
        ]