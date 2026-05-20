from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from ...models import User, Role
from django.contrib.auth import authenticate


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
    



class LoginSerializer(serializers.Serializer):
    mobile_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        mobile_number = attrs.get("mobile_number")
        password = attrs.get("password")

        user = authenticate(
            username=mobile_number,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid mobile number or password")

        if user.is_blocked:
            raise serializers.ValidationError("Your account is blocked")

        if user.is_deleted:
            raise serializers.ValidationError("Your account is deleted")

        if not user.is_active:
            raise serializers.ValidationError("Your account is inactive")

        attrs["user"] = user
        return attrs








class RegisterSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    def validate_mobile_number(self, value):
        if User.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError("Mobile number already exists")
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        role, created = Role.objects.get_or_create(
            slug="user",
            defaults={
                "name": "User",
                "display_name": "User",
                "description": "Default user role",
                "permissions": [],
                "is_default": True,
                "is_active": True,
                "is_deleted": False,
            }
        )

        user = User.objects.create(
            mobile_number=validated_data["mobile_number"],
            email=validated_data.get("email"),
            role=role,
            login_type="mobile",
            password=make_password(validated_data["password"]),
        )

        return user








