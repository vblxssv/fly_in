from pydantic import BaseModel
from typing import List, Dict


class Line(BaseModel):
    line_number: int
    arguments: List[str]
    meta: Dict[str, str]

    def __str__(self) -> str:
        res: str = ''
        res += f"Line {self.line_number}\n"
        res += f"Arguments: {self.arguments}\n"
        res += f"Meta: {self.meta}\n"
        return res
