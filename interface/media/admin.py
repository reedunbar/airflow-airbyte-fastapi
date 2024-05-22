from django.contrib import admin
from .models import Client, YouTubeConnection, WordPressConnection, ClientConnection, LLM, LLMConnection

class ClientConnectionAdmin(admin.ModelAdmin):
    # List of fields to display in the admin interface
    list_display = ('client', 'connection', 'source_id')

    # Make fields read-only in the admin interface
    readonly_fields = ('client', 'connection', 'source_id')

# Register models in Django admin
admin.site.register(Client)
admin.site.register(YouTubeConnection)
admin.site.register(WordPressConnection)
admin.site.register(ClientConnection, ClientConnectionAdmin)
admin.site.register(LLM)
admin.site.register(LLMConnection)