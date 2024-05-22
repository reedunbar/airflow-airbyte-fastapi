from django.db import models
from media.enums import ConnectionType

class Client(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Connection(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

class YouTubeConnection(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    @property
    def connection(self):
        return ConnectionType.YOUTUBE
    playlist_id = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.client.name} - {self.connection}'

class YouTubeVideos(models.Model):
    playlist_id = models.CharField(max_length=100, unique=False)  # Adjust max_length as needed
    video_id = models.CharField(max_length=50, unique=True)  # Adjust max_length as needed
    transcribed = models.BooleanField(default=False)

    def __str__(self):
        return f'Video: {self.video_id}'

class WordPressConnection(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    @property
    def connection(self):
        return ConnectionType.WORDPRESS
    blog_id = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.client.name} - {self.connection}'

class ClientConnection(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE)
    source_id = models.PositiveIntegerField(default=-1)

    def __str__(self):
        return f'{self.client.name} - {self.connection.name} (Source ID: {self.source_id})'


#-----------
# LLM MODELS
#-----------
class LLM(models.Model):
    name = models.CharField(max_length=100)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} - {self.client.name}'

class LLMConnection(models.Model):
    llm = models.ForeignKey(LLM, on_delete=models.CASCADE)
    client_connection = models.ForeignKey(ClientConnection, on_delete=models.CASCADE)
    bucket = models.CharField(max_length=300)
    metadata = models.CharField(max_length=300)

    def __str__(self):
        return f'{self.llm.name} - {self.client_connection}'