from typing import Any, Dict

from pydantic import BaseModel, Field


class StockQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=32)


class AnalysisResponse(BaseModel):
    symbol: str
    name: str
    markdown: str
    mode: str = "legacy"
    data: Dict[str, Any]
