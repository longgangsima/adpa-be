import json

from channels.generic.websocket import AsyncWebsocketConsumer


class GraphQLWSConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for subscription-like real-time pushes.
    Clients send {type: SUBSCRIBE, planId: N} to receive calendar event updates.
    """

    async def connect(self):
        await self.accept()
        self.groups_joined = set()

        await self.send(
            text_data=json.dumps(
                {
                    "type": "WELCOME",
                    "message": "Connected. Send {type: SUBSCRIBE, planId} to start receiving updates.",
                }
            )
        )

    async def disconnect(self, close_code):
        for group in list(self.groups_joined):
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            msg = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps({"type": "ERROR", "message": "Invalid JSON"})
            )
            return

        msg_type = msg.get("type")

        if msg_type == "SUBSCRIBE":
            plan_id = msg.get("planId")
            if not plan_id:
                await self.send(
                    text_data=json.dumps(
                        {"type": "ERROR", "message": "planId required"}
                    )
                )
                return

            group = f"plan_{plan_id}"
            await self.channel_layer.group_add(group, self.channel_name)
            self.groups_joined.add(group)

            await self.send(
                text_data=json.dumps({"type": "SUBSCRIBED", "planId": plan_id})
            )
            return

        if msg_type == "UNSUBSCRIBE":
            plan_id = msg.get("planId")
            group = f"plan_{plan_id}"
            await self.channel_layer.group_discard(group, self.channel_name)
            self.groups_joined.discard(group)
            await self.send(
                text_data=json.dumps({"type": "UNSUBSCRIBED", "planId": plan_id})
            )
            return

        await self.send(
            text_data=json.dumps({"type": "ERROR", "message": "Unknown message type"})
        )

    async def broadcast_message(self, event):
        """Handle messages from channel layer group_send."""
        await self.send(text_data=event["text"])
