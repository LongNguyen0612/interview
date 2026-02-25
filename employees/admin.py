from django.contrib import admin
from .models import (
    Organization, Location, Company, Department,
    Position, Employee, OrganizationColumnConfig
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization']
    list_filter = ['organization']
    search_fields = ['name']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization']
    list_filter = ['organization']
    search_fields = ['name']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization']
    list_filter = ['organization']
    search_fields = ['name']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization']
    list_filter = ['organization']
    search_fields = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'first_name', 'last_name', 'email', 'status',
        'organization', 'department', 'position', 'location'
    ]
    list_filter = ['status', 'organization', 'department', 'location']
    search_fields = ['first_name', 'last_name', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OrganizationColumnConfig)
class OrganizationColumnConfigAdmin(admin.ModelAdmin):
    list_display = ['organization', 'columns']
