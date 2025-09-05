from dataclasses import dataclass
from typing import Dict, Optional



@dataclass
class StockPriceUpdate:
    company: str
    prices: Dict[str, float]  # {"NSE": 101.5, "BSE": 102.2}
    timestamp: str

@dataclass
class ArbitrageSignal:
    company: str
    nse_price: float
    bse_price: float
    diff: float
    recommendation: str  # e.g. "Buy NSE, Sell BSE"

@dataclass
class DraftReport:
    company: str
    summary_md: str
    table_csv: str

@dataclass
class ApproveReport:
    company: str
    approved: bool
    comments: Optional[str] = None

@dataclass
class FetchTick:
    timestamp: str
