from fastapi import FastAPI
import aio_pika
import uvicorn
import asyncio

app = FastAPI()


async def consume():
    connection = await aio_pika.connect_robust("amqp://user:password@localhost/")

    channel = await connection.channel()

    queue = await channel.declare_queue('create_item_queue', durable=True)
    queue_1 = await channel.declare_queue('create_category_queue', durable=True)
    queue_2 = await channel.declare_queue('create_order_queue', durable=True)

    async def callback(message: aio_pika.IncomingMessage):
        async with message.process():
            print(message.body.decode())

    await queue.consume(callback)
    await queue_1.consume(callback)
    await queue_2.consume(callback)

    while True:
        await asyncio.sleep(1)

