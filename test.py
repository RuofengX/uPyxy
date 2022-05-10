import ssl
import asyncio
loop = asyncio.new_event_loop()
loop.create_connection(protocol_factory)
asyncio.open_connection()