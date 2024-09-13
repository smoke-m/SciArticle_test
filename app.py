from fastapi import Depends, FastAPI, WebSocket
from faststream.rabbit.fastapi import RabbitRouter
from pydantic import BaseModel

router = RabbitRouter("amqp://guest:guest@localhost:5672/")

app = FastAPI(
    title='test',
    docs_url='/swagger',
    description='Тестовое задание от SciArticle'
)


class Message(BaseModel):
    user_id: int
    content: str


class User(BaseModel):
    id: int
    name: str


@router.post('/send/{room_id}')
async def send_message(room_id: str, message: Message):
    # Публикуем сообщение в очередь RabbitMQ,
    # используя room_id как ключ маршрутизации
    await router.publish(message.dict(), routing_key=room_id)
    return {"status": "Message sent"}


@router.websocket('/updates/{room_id}')
async def get_updates(
    websocket: WebSocket, room_id: str, user: User = Depends()
):
    await websocket.accept()

    # Подписываемся на очередь RabbitMQ,
    # используя room_id в качестве ключа маршрутизации
    async with router.subscribe(routing_key=room_id) as subscriber:
        async for message in subscriber:
            # Отправляем полученное сообщение пользователю через вебсокет
            await websocket.send_json(message)


app.include_router(router)
