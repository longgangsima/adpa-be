from django.urls import path

from apps.realtime.consumers import GraphQLWSConsumer

websocket_urlpatterns = [
    path("ws/graphql/", GraphQLWSConsumer.as_asgi()),
]
