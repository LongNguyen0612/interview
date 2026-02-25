from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import (
    Organization, Location, Company, Department,
    Position, Employee, OrganizationColumnConfig
)


class EmployeeSearchAPITestCase(APITestCase):
    def setUp(self):
        self.org1 = Organization.objects.create(name='Test Org 1')
        self.org2 = Organization.objects.create(name='Test Org 2')

        self.loc1 = Location.objects.create(name='Singapore', organization=self.org1)
        self.loc2 = Location.objects.create(name='New York', organization=self.org1)
        self.loc3 = Location.objects.create(name='London', organization=self.org2)

        self.comp1 = Company.objects.create(name='Company A', organization=self.org1)
        self.comp2 = Company.objects.create(name='Company B', organization=self.org2)

        self.dept1 = Department.objects.create(name='Engineering', organization=self.org1)
        self.dept2 = Department.objects.create(name='Finance', organization=self.org2)

        self.pos1 = Position.objects.create(name='Developer', organization=self.org1)
        self.pos2 = Position.objects.create(name='Analyst', organization=self.org2)

        self.emp1 = Employee.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@org1.com',
            phone='+1234567890',
            status=Employee.Status.ACTIVE,
            organization=self.org1,
            location=self.loc1,
            company=self.comp1,
            department=self.dept1,
            position=self.pos1
        )

        self.emp2 = Employee.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@org1.com',
            phone='+0987654321',
            status=Employee.Status.NOT_STARTED,
            organization=self.org1,
            location=self.loc2,
            company=self.comp1,
            department=self.dept1,
            position=self.pos1
        )

        self.emp3 = Employee.objects.create(
            first_name='Bob',
            last_name='Wilson',
            email='bob@org1.com',
            status=Employee.Status.TERMINATED,
            organization=self.org1,
            location=self.loc1,
            department=self.dept1
        )

        self.emp4 = Employee.objects.create(
            first_name='Alice',
            last_name='Johnson',
            email='alice@org2.com',
            status=Employee.Status.ACTIVE,
            organization=self.org2,
            location=self.loc3,
            company=self.comp2,
            department=self.dept2,
            position=self.pos2
        )

        OrganizationColumnConfig.objects.create(
            organization=self.org1,
            columns=['first_name', 'last_name', 'email', 'status', 'department']
        )

        self.client = APIClient()
        self.list_url = reverse('employee-list')

    def test_list_employees_requires_organization_id(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_list_employees_for_organization(self):
        response = self.client.get(self.list_url, {'organization_id': self.org1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_organization_isolation(self):
        response = self.client.get(self.list_url, {'organization_id': self.org1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        employee_ids = [emp['id'] for emp in response.data['results']]

        self.assertNotIn(str(self.emp4.id), employee_ids)
        self.assertIn(str(self.emp1.id), employee_ids)
        self.assertIn(str(self.emp2.id), employee_ids)

    def test_filter_by_status(self):
        response = self.client.get(
            self.list_url,
            {
                'organization_id': self.org1.id,
                'status': Employee.Status.ACTIVE
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], str(self.emp1.id))

    def test_filter_by_multiple_statuses(self):
        response = self.client.get(
            self.list_url,
            {
                'organization_id': self.org1.id,
                'status': f'{Employee.Status.ACTIVE},{Employee.Status.NOT_STARTED}'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_include_terminated_employees(self):
        response = self.client.get(
            self.list_url,
            {
                'organization_id': self.org1.id,
                'include_terminated': 'true'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_filter_by_location(self):
        response = self.client.get(
            self.list_url,
            {
                'organization_id': self.org1.id,
                'locations': self.loc1.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], str(self.emp1.id))

    def test_filter_by_department(self):
        response = self.client.get(
            self.list_url,
            {
                'organization_id': self.org1.id,
                'departments': self.dept1.id,
                'include_terminated': 'true'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_search_by_name(self):
        response = self.client.get(
            self.list_url,
            {
                'organization_id': self.org1.id,
                'search': 'John'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'John')

    def test_search_by_email(self):
        response = self.client.get(
            self.list_url,
            {
                'organization_id': self.org1.id,
                'search': 'jane@'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], 'jane@org1.com')

    def test_dynamic_columns(self):
        response = self.client.get(
            self.list_url,
            {'organization_id': self.org1.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if len(response.data['results']) > 0:
            result = response.data['results'][0]
            self.assertIn('first_name', result)
            self.assertIn('last_name', result)
            self.assertIn('email', result)

    def test_pagination(self):
        response = self.client.get(
            self.list_url,
            {
                'organization_id': self.org1.id,
                'include_terminated': 'true'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)


@override_settings(RATE_LIMIT_REQUESTS=5, RATE_LIMIT_WINDOW=60)
class RateLimitTestCase(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Test Org')
        self.client = APIClient()
        self.list_url = reverse('employee-list')

    def test_rate_limiting(self):
        for i in range(5):
            response = self.client.get(
                self.list_url,
                {'organization_id': self.org.id}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            self.list_url,
            {'organization_id': self.org.id}
        )
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('error', response.json())


class ModelTestCase(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Test Org')

    def test_organization_creation(self):
        self.assertEqual(self.org.name, 'Test Org')
        self.assertIsNotNone(self.org.created_at)

    def test_employee_creation(self):
        employee = Employee.objects.create(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            organization=self.org,
            status=Employee.Status.ACTIVE
        )
        self.assertEqual(employee.full_name, 'Test User')
        self.assertEqual(str(employee), 'Test User')

    def test_location_unique_per_organization(self):
        Location.objects.create(name='Singapore', organization=self.org)

        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Location.objects.create(name='Singapore', organization=self.org)

    def test_column_config(self):
        config = OrganizationColumnConfig.objects.create(
            organization=self.org,
            columns=['first_name', 'last_name', 'email']
        )
        self.assertEqual(len(config.columns), 3)
        self.assertIn('first_name', config.columns)
