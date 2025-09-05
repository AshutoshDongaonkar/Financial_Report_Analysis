import asyncio
from autogen_core import RoutedAgent, message_handler, MessageContext, DefaultTopicId
from registered_messages import StockPriceUpdate, ArbitrageSignal, DraftReport, ApproveReport, FetchTick
import json
from pathlib import Path
# ---------------------------
# Agents
# ---------------------------

class PriceFetcherAgent(RoutedAgent):
    def __init__(self, stock_list):
        super().__init__("price-fetcher")
        self.stock_list = stock_list

    async def _fetch_prices(self, company: str):
        # TODO: real NSE/BSE API call
        nse_price = 100.0
        bse_price = 101.5
        return {"NSE": nse_price, "BSE": bse_price}

    @message_handler
    async def on_tick(self, msg: FetchTick, ctx: MessageContext):
        for company in self.stock_list:
            prices = await self._fetch_prices(company)
            await self.publish_message(
                StockPriceUpdate(
                    company=company,
                    prices=prices,
                    timestamp=msg.timestamp
                ),
                ctx.topic_id or DefaultTopicId()
            )

class AnalyzerAgent(RoutedAgent):
    def __init__(self, threshold=0.5):
        super().__init__("analyzer")
        self.threshold = threshold

    @message_handler
    async def on_price_update(self, msg: StockPriceUpdate, ctx: MessageContext):
        nse = msg.prices.get("NSE")
        bse = msg.prices.get("BSE")
        diff = abs(nse - bse)
        if diff >= self.threshold:
            recommendation = "Buy NSE, Sell BSE" if nse < bse else "Buy BSE, Sell NSE"
            await self.publish_message(
                ArbitrageSignal(
                    company=msg.company,
                    nse_price=nse,
                    bse_price=bse,
                    diff=diff,
                    recommendation=recommendation
                ),
                ctx.topic_id or DefaultTopicId()
            )


class ReportAgent(RoutedAgent):
    def __init__(self):
        super().__init__("reporter")

    @message_handler
    async def on_signal(self, msg: ArbitrageSignal, ctx: MessageContext):
        summary = (
            f"## Arbitrage Opportunity for {msg.company}\n"
            f"- NSE: {msg.nse_price}\n"
            f"- BSE: {msg.bse_price}\n"
            f"- Difference: {msg.diff}\n"
            f"- Recommendation: {msg.recommendation}\n"
        )
        table = "exchange,price\nNSE,{:.2f}\nBSE,{:.2f}\n".format(msg.nse_price, msg.bse_price)
        await self.publish_message(
            DraftReport(company=msg.company, summary_md=summary, table_csv=table),
            ctx.topic_id or DefaultTopicId()
        )

    @message_handler
    async def on_approval(self, msg: ApproveReport, ctx: MessageContext):
        if msg.approved:
            print(f"[FINALIZED] Report for {msg.company}")
        else:
            print(f"[REJECTED] Report for {msg.company}: {msg.comments}")