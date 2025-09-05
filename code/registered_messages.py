from dataclasses import dataclass
from typing import Dict, Optional
from pydantic import BaseModel

@dataclass
class StockPriceUpdate(BaseModel):
    company: str
    prices: Dict[str, float]  # {"NSE": 101.5, "BSE": 102.2}
    timestamp: str

@dataclass
class ArbitrageSignal(BaseModel):
    company: str
    nse_price: float
    bse_price: float
    diff: float
    recommendation: str  # e.g. "Buy NSE, Sell BSE"

@dataclass
class DraftReport(BaseModel):
    company: str
    summary_md: str
    table_csv: str

@dataclass
class ApproveReport(BaseModel):
    company: str
    approved: bool
    comments: Optional[str] = None

@dataclass
class FetchTick(BaseModel):
    timestamp: str