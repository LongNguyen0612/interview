from rest_framework import serializers
from .models import (
    Employee, Organization, Location, Company,
    Department, Position, OrganizationColumnConfig
)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name']


class DynamicEmployeeSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    company = CompanySerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    position = PositionSerializer(read_only=True)

    contact_info = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'contact_info',
            'status',
            'location',
            'company',
            'department',
            'position',
        ]

    def get_contact_info(self, obj):
        contact = {
            'email': obj.email,
        }
        if obj.phone:
            contact['phone'] = obj.phone
        return contact

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        column_config = self.context.get('column_config')

        if not column_config:
            return representation

        column_field_mapping = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'email',
            'phone': 'phone',
            'contact_info': 'contact_info',
            'department': 'department',
            'location': 'location',
            'position': 'position',
            'company': 'company',
            'status': 'status',
        }

        filtered_representation = {}

        for column in column_config:
            field_name = column_field_mapping.get(column)
            if field_name and field_name in representation:
                filtered_representation[field_name] = representation[field_name]

        filtered_representation['id'] = representation['id']

        return filtered_representation


class EmployeeSearchSerializer(serializers.Serializer):
    status = serializers.MultipleChoiceField(
        choices=Employee.Status.choices,
        required=False,
        allow_empty=True
    )
    locations = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    companies = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    departments = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    positions = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    search = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Search by name or email"
    )
    include_terminated = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Include terminated employees in results"
    )
