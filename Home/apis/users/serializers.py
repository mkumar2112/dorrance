from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from ...models import User


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "uuid",
            "username",
            "mobile_number",
            "email",
            "first_name",
            "last_name",
            "role",
            "role_name",
            "is_mobile_verified",
            "is_email_verified",
            "login_type",
            "last_login_ip",
            "last_login_device",
            "is_blocked",
            "blocked_reason",
            "blocked_at",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_deleted",
            "date_joined",
            "last_login",
            "password",
        ]

        read_only_fields = [
            "id",
            "uuid",
            "role_name",
            "last_login_ip",
            "last_login_device",
            "blocked_at",
            "date_joined",
            "last_login",
        ]

        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": False,
                "allow_blank": True,
            }
        }

    def get_role_name(self, obj):
        if obj.role:
            return obj.role.display_name or obj.role.name
        return None

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        user = User(**validated_data)

        if password:
            user.password = make_password(password)
        else:
            user.set_unusable_password()

        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.password = make_password(password)

        instance.save()
        return instance