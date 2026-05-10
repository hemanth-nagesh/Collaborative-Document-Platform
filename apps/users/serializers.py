from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class UserSerializer(serializers.ModelSerializer):
    # Override to enforce email format + (optional) case-insensitive uniqueness
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), lookup='iexact')]
    )

    # Enforce digits-only (optional leading +), 10–15 digits
    phone = serializers.RegexField(
        regex=r'^\+?\d{10,15}$',
        validators=[UniqueValidator(queryset=User.objects.all())],
        error_messages={'invalid': 'Phone must be 10–15 digits (optional leading +).'},
    )

    def validate_first_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('First name cannot be blank.')
        return value

    def validate_email(self, value):
        # runs after EmailField validation; normalize before saving
        return value.strip().lower()

    def validate(self, attrs):
        # example cross-field rule (optional)
        if attrs.get('first_name', '').lower() == attrs.get('last_name', '').lower():
            raise serializers.ValidationError({'last_name': 'Last name must differ from first name.'})
        return attrs

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'created_at']
        read_only_fields = ['id', 'created_at']
