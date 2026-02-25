import uuid
from django.db import models


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'organizations'
        ordering = ['name']

    def __str__(self):
        return self.name


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='locations'
    )

    class Meta:
        db_table = 'locations'
        ordering = ['name']
        unique_together = [['name', 'organization']]
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='companies'
    )

    class Meta:
        db_table = 'companies'
        verbose_name_plural = 'companies'
        ordering = ['name']
        unique_together = [['name', 'organization']]
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='departments'
    )

    class Meta:
        db_table = 'departments'
        ordering = ['name']
        unique_together = [['name', 'organization']]
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Position(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='positions'
    )

    class Meta:
        db_table = 'positions'
        ordering = ['name']
        unique_together = [['name', 'organization']]
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Employee(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        NOT_STARTED = 'not_started', 'Not Started'
        TERMINATED = 'terminated', 'Terminated'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='employees'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )

    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'last_name', 'first_name']),
            models.Index(fields=['organization', 'location']),
            models.Index(fields=['organization', 'company']),
            models.Index(fields=['organization', 'department']),
            models.Index(fields=['organization', 'position']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class OrganizationColumnConfig(models.Model):
    AVAILABLE_COLUMNS = [
        ('first_name', 'First Name'),
        ('last_name', 'Last Name'),
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('contact_info', 'Contact Info'),
        ('department', 'Department'),
        ('location', 'Location'),
        ('position', 'Position'),
        ('company', 'Company'),
        ('status', 'Status'),
    ]

    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='column_config',
        primary_key=True
    )

    columns = models.JSONField(
        default=list,
        help_text="List of columns to display in order"
    )

    class Meta:
        db_table = 'organization_column_configs'

    def __str__(self):
        return f"Column config for {self.organization.name}"
