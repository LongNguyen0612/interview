from django.core.management.base import BaseCommand
from employees.models import (
    Organization, Location, Company, Department,
    Position, Employee, OrganizationColumnConfig
)


class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        org1 = Organization.objects.create(name='Tech Corp')
        org2 = Organization.objects.create(name='Finance Inc')

        OrganizationColumnConfig.objects.create(
            organization=org1,
            columns=[
                'first_name', 'last_name', 'contact_info',
                'department', 'location', 'position', 'status'
            ]
        )
        OrganizationColumnConfig.objects.create(
            organization=org2,
            columns=[
                'first_name', 'last_name', 'department',
                'location', 'position'
            ]
        )

        loc1_org1 = Location.objects.create(name='Singapore', organization=org1)
        loc2_org1 = Location.objects.create(name='Oxhere', organization=org1)
        loc3_org1 = Location.objects.create(name='New York', organization=org1)

        loc1_org2 = Location.objects.create(name='London', organization=org2)
        loc2_org2 = Location.objects.create(name='Tokyo', organization=org2)

        comp1_org1 = Company.objects.create(name='Tech Corp Main', organization=org1)
        comp2_org1 = Company.objects.create(name='Tech Corp Asia', organization=org1)
        comp1_org2 = Company.objects.create(name='Finance Inc Global', organization=org2)

        dept1_org1 = Department.objects.create(name='Engineering', organization=org1)
        dept2_org1 = Department.objects.create(name='Marketing', organization=org1)
        dept3_org1 = Department.objects.create(name='Sales', organization=org1)
        dept1_org2 = Department.objects.create(name='Finance', organization=org2)
        dept2_org2 = Department.objects.create(name='Accounting', organization=org2)

        pos1_org1 = Position.objects.create(name='Software Engineer', organization=org1)
        pos2_org1 = Position.objects.create(name='Assistant Manager', organization=org1)
        pos3_org1 = Position.objects.create(name='Senior Developer', organization=org1)
        pos1_org2 = Position.objects.create(name='Financial Analyst', organization=org2)
        pos2_org2 = Position.objects.create(name='Accountant', organization=org2)

        employees_org1 = [
            {
                'first_name': '005Test',
                'last_name': '005',
                'email': '005@techcorp.com',
                'phone': '+65-1234-5678',
                'status': Employee.Status.ACTIVE,
                'location': loc1_org1,
                'company': comp1_org1,
                'department': dept1_org1,
                'position': pos2_org1,
                'organization': org1,
            },
            {
                'first_name': '007Test',
                'last_name': '007',
                'email': '007@techcorp.com',
                'phone': '+65-1234-5679',
                'status': Employee.Status.ACTIVE,
                'location': None,
                'company': None,
                'department': None,
                'position': None,
                'organization': org1,
            },
            {
                'first_name': 'ava preferred',
                'last_name': 'last',
                'email': 'ava@techcorp.com',
                'phone': '',
                'status': Employee.Status.ACTIVE,
                'location': None,
                'company': None,
                'department': None,
                'position': None,
                'organization': org1,
            },
            {
                'first_name': 'Amanda',
                'last_name': 'Cerny',
                'email': 'amanda@techcorp.com',
                'phone': '+65-9999-8888',
                'status': Employee.Status.ACTIVE,
                'location': loc2_org1,
                'company': comp1_org1,
                'department': dept1_org1,
                'position': pos2_org1,
                'organization': org1,
            },
            {
                'first_name': 'AnaTest',
                'last_name': 'Profile',
                'email': 'ana@techcorp.com',
                'phone': '',
                'status': Employee.Status.ACTIVE,
                'location': None,
                'company': None,
                'department': None,
                'position': None,
                'organization': org1,
            },
            {
                'first_name': 'Amelia',
                'last_name': 'Smith',
                'email': 'amelia@techcorp.com',
                'phone': '+65-1111-2222',
                'status': Employee.Status.ACTIVE,
                'location': loc3_org1,
                'company': comp2_org1,
                'department': dept2_org1,
                'position': pos1_org1,
                'organization': org1,
            },
        ]

        for emp_data in employees_org1:
            Employee.objects.create(**emp_data)

        employees_org2 = [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@financeinc.com',
                'phone': '+44-2000-1111',
                'status': Employee.Status.ACTIVE,
                'location': loc1_org2,
                'company': comp1_org2,
                'department': dept1_org2,
                'position': pos1_org2,
                'organization': org2,
            },
            {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane@financeinc.com',
                'phone': '+81-3-1234-5678',
                'status': Employee.Status.NOT_STARTED,
                'location': loc2_org2,
                'company': comp1_org2,
                'department': dept2_org2,
                'position': pos2_org2,
                'organization': org2,
            },
            {
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'email': 'bob@financeinc.com',
                'phone': '+44-2000-2222',
                'status': Employee.Status.TERMINATED,
                'location': loc1_org2,
                'company': comp1_org2,
                'department': dept1_org2,
                'position': pos1_org2,
                'organization': org2,
            },
        ]

        for emp_data in employees_org2:
            Employee.objects.create(**emp_data)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created:\n'
            f'  - 2 organizations\n'
            f'  - {Location.objects.count()} locations\n'
            f'  - {Company.objects.count()} companies\n'
            f'  - {Department.objects.count()} departments\n'
            f'  - {Position.objects.count()} positions\n'
            f'  - {Employee.objects.count()} employees'
        ))
