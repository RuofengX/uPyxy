class SyncLogger():
    """这是aisle在uPy下的简易替代方案"""
    def __init__(self, name: str = None):
        self.name = name
        
    def debug(self, msg: str) -> None:
        print(self.name + '> DEBUG: ' + msg)
    
    def info(self, msg: str) -> None:
        print(self.name + '> INFO: ' + msg)
        
    def warning(self, msg: str) -> None:
        print(self.name + '> WARNING: ' + msg)
        
    def error(self, msg: str) -> None:
        print(self.name + '> ERROR: ' + msg)
        
    def critical(self, msg: str) -> None:
        print(self.name + '> CRITICAL: ' + msg)
    
    
    def get_child(self, suffix: str):
        return self.__class__(f"{self.name}.{suffix}")
    
    def set_level(self, level: str):
        """由于所有串口输出都是DEBUG级别，所以没有必要再分等级输出"""
        pass
        
class LogMixin():
    def __init__(self):
        self.logger = SyncLogger(self.__class__.__name__)
        
LOG = SyncLogger("LOG")
    
    