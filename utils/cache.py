import os
import plyvel

class Cache:
    _instance = None
    _db_path = ".cache/asset"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._db = cls._instance.init()
        return cls._instance

    def init(self):
        if not os.path.exists(self._db_path):
            os.makedirs(self._db_path)
        return plyvel.DB(self._db_path, create_if_missing=True)

    def store_text(self, text, file_path):
        text_bytes = text.encode('utf-8')
        file_path_bytes = file_path.encode('utf-8')
        self._db.put(text_bytes, file_path_bytes)
    
    def delete_entry(self, text):
        if self._db.get(text.encode('utf-8')):
            self._db.delete(text.encode('utf-8'))
            print(f"Deleted cache entry for text: {text}")
        else:
            print(f"Cache entry for text '{text}' does not exist")


    def get_file_path(self, text):
        text_bytes = text.encode('utf-8')
        file_path_bytes = self._db.get(text_bytes)
        if file_path_bytes:
            return file_path_bytes.decode('utf-8')
        else:
            return None

    def close(self):
        self._db.close()


    def close(self):
        self._db.close()
 