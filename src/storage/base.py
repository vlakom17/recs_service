import csv
import uuid
from typing import List, Dict
from pydantic import BaseModel

class csvRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path

