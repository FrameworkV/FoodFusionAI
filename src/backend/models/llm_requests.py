from pydantic import BaseModel

class DummyRequest(BaseModel):
    request: str