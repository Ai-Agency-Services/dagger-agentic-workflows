from typing import List, Optional
from pydantic import BaseModel

class CodeSymbol(BaseModel):
    name: str
    type: str
    line_number: int
    column: int
    end_line_number: Optional[int] = None
    end_column: Optional[int] = None
    scope: Optional[str] = None
    signature: Optional[str] = None
    visibility: Optional[str] = None

class CodeFile(BaseModel):
    content: str
    filepath: str
    language: str
    symbols: List[CodeSymbol] = []