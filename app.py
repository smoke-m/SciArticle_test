from fastapi import Depends, FastAPI, WebSocket
from faststream.rabbit.fastapi import RabbitRouter, Logger
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


class Room(BaseModel):
    users_count: int


async def count_dep(room: Room) -> bool:
    return room.users_count == 2


@router.post('/send/{room_id}')
async def send_message(
    room_id: str,
    message: Message,
    logger: Logger,
    dep: bool = Depends(count_dep)
):
    # Публикуем сообщение в очередь RabbitMQ,
    # используя room_id как ключ маршрутизации
    assert dep is True
    await router.publisher(message.dict(), routing_key=room_id,)
    logger.info({"status": "Message sent"})
    return {"status": "Message sent"}


@router.websocket('/updates/{room_id}')
async def get_updates(
    websocket: WebSocket,
    room_id: str,
    logger: Logger,
    user: User = Depends(),
):
    await websocket.accept()

    # Подписываемся на очередь RabbitMQ,
    # используя room_id в качестве ключа маршрутизации
    async with router.subscriber(routing_key=room_id) as subscriber:
        async for message in subscriber:
            # Отправляем полученное сообщение пользователю через вебсокет
            await websocket.send_json(message)
            logger.info("Message sent")


app.include_router(router)


# технология faststream для меня новая, мною не изученная
# т.з. делал рукаводсвуясь статьями в хабр
# оссновной стек перечисленный в вакансии практиковал
# в портфолио есть проекты
# с уважением Михаил
