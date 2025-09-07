from pydantic import BaseModel
from datetime import datetime
#from autogen_agentchat.messages import StructuredMessage


class FetchTick(BaseModel):
    timestamp: datetime


class StockPriceUpdate(BaseModel):
    company: str
    nse_price: float
    bse_price: float
    timestamp: str


class ArbitrageSignal(BaseModel):
    company: str
    nse_price: float
    bse_price: float
    arbitrage: float
    timestamp: str


class ReportDraft(BaseModel):
    report_id: str
    content: str


class ApproveReport(BaseModel):
    report_id: str
    approved: bool
    comments: str | None = None


