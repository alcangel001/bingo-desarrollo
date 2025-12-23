from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/messages/$', consumers.MessageConsumer.as_asgi()),
    re_path(r'ws/bingo/(?P<user_id>\d+)/$', consumers.BingoConsumer.as_asgi()),
    re_path(r'ws/user/(?P<user_id>\d+)/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/game/(?P<game_id>\d+)/$', consumers.BingoConsumer.as_asgi()),
    re_path(r'ws/lobby/$', consumers.LobbyConsumer.as_asgi()),
    re_path(r'ws/raffle/(?P<raffle_id>\d+)/$', consumers.RaffleConsumer.as_asgi()),
    # Módulo de Dados
    re_path(r'ws/dice/game/(?P<room_code>[A-Z0-9]+)/$', consumers.DiceGameConsumer.as_asgi()),
]