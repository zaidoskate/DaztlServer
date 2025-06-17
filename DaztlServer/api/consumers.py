from channels.generic.websocket import AsyncWebsocketConsumer
import json

connected_clients = set()
connected_clients_chat = set()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        connected_clients.add(self)
        print(f"Cliente conectado. Total: {len(connected_clients)}")

    async def disconnect(self, close_code):
        connected_clients.remove(self)
        print(f"Cliente desconectado. Total: {len(connected_clients)}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        print("Mensaje recibido del cliente:", data)

    async def send_personal(self, message):
        await self.send(text_data=json.dumps(message))

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        connected_clients_chat.add(self)
        print(f"Cliente conectado. Total: {len(connected_clients_chat)}")

    async def disconnect(self, close_code):
        connected_clients_chat.remove(self)
        print(f"Cliente desconectado. Total: {len(connected_clients_chat)}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        print("Mensaje recibido del cliente:", data)

    async def send_personal(self, message):
        await self.send(text_data=json.dumps(message))
