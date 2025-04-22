from pydantic import BaseModel

class UserMessage(BaseModel):
    type: str
    group: str = ""
    target: str = ""
