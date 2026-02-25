from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Employee, OrganizationColumnConfig
from .serializers import DynamicEmployeeSerializer, EmployeeSearchSerializer


class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DynamicEmployeeSerializer

    def get_queryset(self):
        organization_id = self.request.query_params.get('organization_id')

        if not organization_id:
            return Employee.objects.none()

        queryset = Employee.objects.filter(
            organization_id=organization_id
        ).select_related(
            'location',
            'company',
            'department',
            'position',
            'organization'
        )

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()

        organization_id = self.request.query_params.get('organization_id')
        if organization_id:
            try:
                config = OrganizationColumnConfig.objects.get(
                    organization_id=organization_id
                )
                context['column_config'] = config.columns
            except OrganizationColumnConfig.DoesNotExist:
                context['column_config'] = [
                    'first_name',
                    'last_name',
                    'contact_info',
                    'department',
                    'location',
                    'position',
                    'status'
                ]

        return context

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='organization_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Organization ID (required for all requests)',
                required=True
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by employee status (comma-separated: active,not_started,terminated)',
                required=False,
                many=True
            ),
            OpenApiParameter(
                name='locations',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by location IDs (comma-separated)',
                required=False,
                many=True
            ),
            OpenApiParameter(
                name='companies',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by company IDs (comma-separated)',
                required=False,
                many=True
            ),
            OpenApiParameter(
                name='departments',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by department IDs (comma-separated)',
                required=False,
                many=True
            ),
            OpenApiParameter(
                name='positions',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by position IDs (comma-separated)',
                required=False,
                many=True
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search by name or email',
                required=False
            ),
            OpenApiParameter(
                name='include_terminated',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Include terminated employees',
                required=False
            ),
        ],
        description='Search employees with various filter options'
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = self.apply_filters(queryset, request)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def apply_filters(self, queryset, request):
        status_params = request.query_params.getlist('status')
        if status_params:
            statuses = []
            for s in status_params:
                statuses.extend(s.split(','))
            if statuses:
                queryset = queryset.filter(status__in=statuses)

        include_terminated = request.query_params.get('include_terminated', 'false').lower() == 'true'
        if not include_terminated and not status_params:
            queryset = queryset.exclude(status=Employee.Status.TERMINATED)

        location_params = request.query_params.getlist('locations')
        if location_params:
            location_ids = []
            for loc in location_params:
                location_ids.extend(loc.split(','))
            if location_ids:
                queryset = queryset.filter(location_id__in=location_ids)

        company_params = request.query_params.getlist('companies')
        if company_params:
            company_ids = []
            for comp in company_params:
                company_ids.extend(comp.split(','))
            if company_ids:
                queryset = queryset.filter(company_id__in=company_ids)

        department_params = request.query_params.getlist('departments')
        if department_params:
            department_ids = []
            for dept in department_params:
                department_ids.extend(dept.split(','))
            if department_ids:
                queryset = queryset.filter(department_id__in=department_ids)

        position_params = request.query_params.getlist('positions')
        if position_params:
            position_ids = []
            for pos in position_params:
                position_ids.extend(pos.split(','))
            if position_ids:
                queryset = queryset.filter(position_id__in=position_ids)

        search = request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )

        return queryset
