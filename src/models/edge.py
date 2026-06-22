from pydantic import BaseModel


class Edge(BaseModel):
    target: str
    capacity: int
