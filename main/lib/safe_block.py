import aisle
import uuid
import json
import time
import cryptolib

# debug
# from pympler import asizeof
# import sys
# from objprint import op


class Key:
    """用来加解密的key

    Raises:
        TypeError: 如果__set__传入了非bytes类型
        ValueError: 如果__set__传入非16位

    Returns:
        self: 一个16位比特串
    """

    __slots__ = "_key_bytes"

    def __init__(self, key_string: str = "") -> None:
        if not key_string:
            key_string = str(uuid.uuid4().hex)
        self.key_bytes = key_string.encode("utf-8")
        pass

    @property
    def key_bytes(self) -> bytes:
        return self._key_bytes

    @key_bytes.setter
    def key_bytes(self, value: bytes):
        if not isinstance(value, bytes):
            raise TypeError("key must be bytes")
        elif len(value) != 32:
            raise ValueError("key must be 32 bytes")
        else:
            self._key_bytes = value

    @property
    def key_string(self) -> str:
        return self.key_bytes.decode()

    @key_string.setter
    def key_string(self, value: str):
        self.key_bytes = value.encode("utf-8")


class DecryptError(Exception):
    """解密错误"""

    pass

class Crypto:
    #TODO: 需要测试
     
    __slots__ = ["cipher"]

    def __init__(self, key_bytes: bytes) -> None:
        super().__init__()
        self.cipher = cryptolib.aes(key_bytes, 1)  # 1表示AES-ECB
        # self.block_size = 32

    def encrypt(self, b: bytes) -> bytes:
        """输入的字节串无需填充"""
        return self.cipher.encrypt(self._pad(b, 16))

    def decrypt(self, b: bytes) -> bytes:
        try:
            return self._unpad(self.cipher.decrypt(b))
        except ValueError:
            """解密错误，解密失败"""
            raise DecryptError("解密错误")

    @staticmethod
    def _pad(b: bytes, blk_size) -> bytes:
        """将字节串填充到blk_size的倍数"""
        print(f"DEBUG: 将要pad {b}")
        b += b"\x01"
        
        if len(b) % blk_size == 0:
            return b
        else:            
            return b + b'\x00' * (blk_size - len(b) % blk_size)
        
    @staticmethod
    def _unpad(b: bytes) -> bytes:
        """将字节串去掉填充"""
        print(f"DEBUG: 将要unpad {b}")
        for i in range(len(b) - 1, 0, -1):
            # 此时遍历的元素下标为[i-1]
            if b[i - 1] == 0:
                b = b[:i - 1]
            else:
                break

        b = b[:-1]  # 再去掉一个占位符
        return b
    
    
class Block:
    """安全区块"""

    __slots__ = "uuid", "key", "payload", "timestamp", "_crypto"

    @classmethod
    def from_bytes(cls, key: Key, b: bytes) -> "Block":
        """解密字节串并转换为Block对象

        Args:
            key (Key): 加密密钥

        Raises:
            DecryptError: 解密错误，解密失败
        """
        crypto = Crypto(key.key_bytes)
        rebuild_dict = json.loads(crypto.decrypt(b).decode("utf-8"))
        vTime = rebuild_dict["timestamp"] - int(time.time())  # 验证时间是否大于10秒
        if vTime >= 10:
            raise DecryptError("时间戳误差大于10秒")

        rtn = cls(key, {})  # 创建空的Block对象
        rtn.uuid = rebuild_dict["uuid"]  # 强制重载
        rtn.payload = rebuild_dict["payload"]  # 强制重载
        rtn.timestamp = rebuild_dict["timestamp"]

        return rtn

    def __init__(self, key: Key, payload: dict = {}) -> None:
        """安全区块构造函数"""
        super().__init__()

        # 四个参数（简称ukpt）都会加密
        self.uuid = uuid.uuid4().hex
        self.key = key.key_string
        self.payload = payload
        self.timestamp = int(time.time())
        self._crypto = Crypto(key.key_bytes)  #TODO: 可以改为单例
        pass

    @property
    def block_bytes(self) -> bytes:
        """自我加密后，返回ukpt的字节串"""
        rtn = self._crypto.encrypt(json.dumps(self.__ukpt).encode("utf-8"))
        return rtn

    def __enter__(self) -> "Block":
        """返回自身"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """减小内存消耗 但是在upy中不会在with语句退出时运行"""
        del self

    @property
    def __ukpt(self) -> dict:
        # ukpt取首字母
        return {
            "uuid": self.uuid,
            "key": self.key,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }




def test():
    # pad测试
    crypto = Crypto(b"1234567890123456")
    target = b'123456000'
    print("pad " + str(target))
    print(crypto._pad(target, 16))
    print("unpad " + str(target))
    print(crypto._unpad(crypto._pad(target, 16)))
    print("pad test done")
    
    key = Key()
    print(key.key_bytes)
    blk = Block(key, {"a": 1})
    print(blk.block_bytes)
    Block.from_bytes(key, blk.block_bytes)
    pass


if __name__ == "__main__":
    test()
