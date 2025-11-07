import os
from faststream.rabbit.fastapi import RabbitRouter


rabbit_url = os.getenv("RABBIT_URL") or "amqp://guest:guest@localhost:5672/"

rabbit_router = RabbitRouter(rabbit_url)
