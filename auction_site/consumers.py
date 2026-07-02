# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.room_group_name = f'auction_{self.auction_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Gửi giá mới tới tất cả người dùng trong group
    async def send_new_bid(self, event):
        await self.send(text_data=json.dumps({'current_price': event['current_price'],
                                              'next_bid': event['next_bid'],
                                              'bid_html': event['bid_html']}))