from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Connection, YouTubeConnection, WordPressConnection, ClientConnection
from media.enums import ConnectionType

@receiver(post_save, sender=YouTubeConnection)
def create_client_connection_from_youtube(sender, instance, created, **kwargs):
    if created:
        youtube_connection_type = Connection.objects.get(name=ConnectionType.YOUTUBE)
        ClientConnection.objects.create(
            client=instance.client,
            connection=youtube_connection_type,
            source_id=instance.id
        )


@receiver(post_save, sender=WordPressConnection)
def create_client_connection_from_wordpress(sender, instance, created, **kwargs):
    if created:
        wordpress_connection_type = Connection.objects.get(name=ConnectionType.WORDPRESS)
        ClientConnection.objects.create(
            client=instance.client,
            connection=wordpress_connection_type,
            source_id=instance.id
        )

@receiver(pre_delete, sender=YouTubeConnection)
def handle_youtube_connection_delete(sender, instance, **kwargs):
    # Retrieve the corresponding ClientConnection and delete it
    try:
        client_connection = ClientConnection.objects.get(client_id=instance.client, connection__name=ConnectionType.YOUTUBE, source_id=instance.id)
        client_connection.delete()
        print(f'Client connection deleted for YouTube connection: {client_connection}')
    except ClientConnection.DoesNotExist:
        # Handle the case where ClientConnection is not found
        print('Error: Client connection not found for YouTube connection')

@receiver(pre_delete, sender=WordPressConnection)
def handle_wordpress_connection_delete(sender, instance, **kwargs):
    # Retrieve the corresponding ClientConnection and delete it
    try:
        client_connection = ClientConnection.objects.get(client_id=instance.client, connection__name=ConnectionType.WORDPRESS, source_id=instance.id)
        client_connection.delete()
        print(f'Client connection deleted for WordPress connection: {client_connection}')
    except ClientConnection.DoesNotExist:
        # Handle the case where ClientConnection is not found
        print('Error: Client connection not found for WordPress connection')