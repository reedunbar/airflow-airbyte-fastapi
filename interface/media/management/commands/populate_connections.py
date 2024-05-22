from django.core.management.base import BaseCommand
from media.models import Connection
from media.enums import ConnectionType

class Command(BaseCommand):
    help = 'Populate predefined connection types'

    def handle(self, *args, **options):
        # Define predefined connection types
        predefined_connections = [
            ConnectionType.YOUTUBE,
            ConnectionType.WORDPRESS,
            # Add more connection types as needed
        ]

        # Create Connection instances for each predefined type
        for connection_type in predefined_connections:
            Connection.objects.get_or_create(name=connection_type)

        self.stdout.write(self.style.SUCCESS('Successfully populated connection types'))