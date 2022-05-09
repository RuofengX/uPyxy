class SyncLogger():
    def __init__(self, name: str = None):
        self.name = name
        
    def debug(self, msg: str) -> None:
        print('DEBUG: ' + msg)
    
    def info(self, msg: str) -> None:
        print('INFO: ' + msg)
        
    def warning(self, msg: str) -> None:
        print('WARNING: ' + msg)
        
    def error(self, msg: str) -> None:
        print('ERROR: ' + msg)
        
    def critical(self, msg: str) -> None:
        print('CRITICAL: ' + msg)
    
    
    def get_child(self, suffix: str):
        return self.__class__(f"{self.name}.{suffix}")
    
class LogMixin():
    def __init__(self):
        self.logger = SyncLogger(self.__name__)
        
LOG = SyncLogger("LOG")
    
    