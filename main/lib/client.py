"""
Filename: client.py
"""
import uasyncio
from safe_block import Block, DecryptError
from xybase import StreamBase
from aisle import SyncLogger
import ssl

class RemoteClientError(Exception):
    """和远程连接的客户端对象错误"""

    def __init__(self, msg: str = None):
        super().__init__(msg)
        self.message = msg

    def __str__(self) -> str:
        return f"RemoteClientError: {self.message}"


class Client(StreamBase):
    """维护和远程的连接"""

    def __init__(
        self,
        key: str,
        remoteAddr: str,
        remotePort: int,
        tag = None,  # Optional[Union[str, int]]
    ) -> None:
        super().__init__(key=key)
        if tag:
            self.logger: SyncLogger = self.logger.getChild(f"{tag}")
        self.remote_addr = remoteAddr
        self.remote_port = remotePort
        self.remote_reader: uasyncio.StreamReader
        self.remote_writer: uasyncio.StreamWriter

    # HACK: 需要优化内存，减小长连接的内存占用

    async def remote_handshake(self, payload: dict) -> tuple:
        """打开一个连接之前的预协商"""

        try:
            with Block(self.key, payload) as block:
                buf = block.block_bytes
                response = await self.__exchange_block(buf)

            response_block = Block.from_bytes(self.key, response)

            bind_address, bind_port = (
                response_block.payload["bind_address"],
                response_block.payload["bind_port"],
            )
            self.logger.info("预协商成功")
            if (bind_address == "") or (bind_port == 0):
                raise RemoteClientError("远程的连接建立失败")

            rtn = bind_address, bind_port
            self.logger.debug(f"远程已创建连接，地址：{bind_address}，端口：{bind_port}")
            return rtn

        # except ConnectionResetError:  # uPy下的ConnectionResetError不存在
        # 
        #     self.logger.info("远程连接关闭")
        #     await self.remote_close()
        #     return None, None

        except DecryptError as error:
            self.logger.info(f"预协商解密时发生错误 {error}")
            await self.remote_close()
            return None, None

        # except ConnectionRefusedError:  # uPy下的ConnectionRefusedError不存在
        #     self.logger.info("远程连接失败")
        #     # 因为远程连接没有创建，所以不用关闭
        #     # await self.remote_close()
        #     return None, None

        except Exception as error:
            self.logger.warning(f"其他错误 > {type(error)}|{error}")
            await self.remote_close()
            raise error

    async def remote_close(self) -> None:
        """关闭远程的连接

        捕获所有异常"""
        if hasattr(self, 'remote_writer'):
            await self.try_close(self.remote_writer)

    async def __exchange_block(self, raw: bytes) -> bytes:
        """远程的连接预协商，self.reader和writer初始化"""
        self.remote_reader, self.remote_writer = await self.__connect()

        self.remote_writer.write(raw)
        await self.remote_writer.drain()
        rtn = await self.remote_reader.read(4096)

        return rtn

    async def __connect(self):  # -> Coroutine[None, None, Tuple[StreamReader, StreamWriter]]
        rtn = await uasyncio.open_connection(
            self.remote_addr,
            self.remote_port,
            # ssl=True,  # HACK: uasyncio.open_connection不支持ssl，需要自己实现
            # TODO: 等待上游实现ssl https://github.com/micropython/micropython/issues/8647
        )
        
        
        return rtn

    
    