from autogen_core import RoutedAgent, type_subscription,message_handler, MessageContext, DefaultTopicId, TopicId
from registered_messages import StockPriceUpdate, ArbitrageSignal, ApproveReport, FetchTick, ReportDraft
from autogen_agentchat.messages import StructuredMessage
from constants import STOCK_UPDATE_TOPIC
import logging

#STOCK_UPDATE_TOPIC = TopicId(type="stock_updates", source="nse_bse_feed")

# 1. Price Fetcher
@type_subscription(topic_type=STOCK_UPDATE_TOPIC.type)
class PriceFetcherAgent(RoutedAgent):
    produced_message_types = [StructuredMessage[StockPriceUpdate ]]

    def __init__(self, stock_list: list[str], description: str):
        super().__init__(description=description)
        self.stock_list = stock_list
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.info(f"Initialized PriceFetcher with stocks: {self.stock_list}")

    async def _fetch_prices(self, company: str):
        # TODO: replace with NSE/BSE API calls
        self.log.info(f"Fetching prices for {company}...")
        nse_price = 100.0
        bse_price = 101.5
        return {"NSE": nse_price, "BSE": bse_price}

    @message_handler
    async def on_tick(self, message: StructuredMessage[FetchTick], ctx: MessageContext)->None:
        self.log.info(f"PriceFetcherAgent received tick message from {message.source}")
        print("Handler successfully called.")
        payload = message.content
        for company in self.stock_list:
            prices = await self._fetch_prices(company)
            stock_data = StockPriceUpdate(
                        company=company,
                        nse_price=prices["NSE"],
                        bse_price=prices["BSE"],
                        timestamp=payload.timestamp)

            stock_message = StructuredMessage[StockPriceUpdate](
                content=stock_data,
                source="stock_bot_agent"
            )
            #stock_topic_id = DefaultTopicId(source="stock_updates")
            # Explicitly define the topic type and source
            #stock_topic_id = TopicId(topic_type="stock_updates", topic_source="nse_bse")
            await self.publish_message(message=stock_message, topic_id=STOCK_UPDATE_TOPIC)
            self.log.info(f"Published stock price update for {company} to topic {STOCK_UPDATE_TOPIC.type}")
            print(f"Published stock price update for {company} to topic {STOCK_UPDATE_TOPIC.type}")

# 2. Analyzer
@type_subscription(topic_type=STOCK_UPDATE_TOPIC.type)
class AnalyzerAgent(RoutedAgent):
    produced_message_types = [ArbitrageSignal]

    def __init__(self, description: str):
        super().__init__(description=description)
        self.log = logging.getLogger(self.__class__.__name__)

    @message_handler
    async def on_price_update(self, message: StructuredMessage[StockPriceUpdate], ctx: MessageContext)->None:
        self.log.info(f"AnalyzerAgent received tick message from {message.source}")
        payload = message.content
        arbitrage = abs(payload.nse_price - payload.bse_price)
        if arbitrage > 0.5:  # simple threshold
            arbitrage_data = ArbitrageSignal(
                        company=payload.company,
                        nse_price=payload.nse_price,
                        bse_price=payload.bse_price,
                        arbitrage=arbitrage,
                        timestamp=payload.timestamp
                    )
            #arbitrage_topic_id = DefaultTopicId(source="arbitrage_updates")
            arbitrage_message = StructuredMessage[ArbitrageSignal](
                content=arbitrage_data,
                source="arbitrage_bot_agent"
            )
            await self.publish_message(message=arbitrage_message, topic_id=STOCK_UPDATE_TOPIC)
            self.log.info(f"Published ArbitrageSignal to topic {STOCK_UPDATE_TOPIC.type}")
            print(f"Published ArbitrageSignal to topic {STOCK_UPDATE_TOPIC.type}")


# 3. Reporter
@type_subscription(topic_type=STOCK_UPDATE_TOPIC.type)
class ReportGeneratorAgent(RoutedAgent):
    produced_message_types = [ReportDraft]

    def __init__(self, description: str):
        super().__init__(description=description)
        self.log = logging.getLogger(self.__class__.__name__)

    @message_handler
    async def on_signal(self, message: StructuredMessage[ArbitrageSignal], ctx: MessageContext)->None:
        self.log.info(f"ReportGeneratorAgent received tick message from {message.source}")
        payload = message.content
        report_text = (
            f"Report for {payload.company}: NSE={payload.nse_price}, "
            f"BSE={payload.bse_price}, Arbitrage={payload.arbitrage}"
        )
        draft_data = ReportDraft(report_id=f"RPT-{payload.company}-{payload.timestamp}",
                    content=report_text)
        draft_message = StructuredMessage[ReportDraft](
                content=draft_data,
                source="report_generator_bot_agent"
            )
        #report_topic_id = DefaultTopicId(source="draft_report_updates")
        await self.publish_message(message=draft_message, topic_id=STOCK_UPDATE_TOPIC)
        self.log.info(f"Published message to generate report to topic {STOCK_UPDATE_TOPIC.type}")
        print(f"Published message to generate report to topic {STOCK_UPDATE_TOPIC.type}")


# 4. Manager
@type_subscription(topic_type=STOCK_UPDATE_TOPIC.type)
class ManagerAgent(RoutedAgent):
    produced_message_types = [ApproveReport]

    def __init__(self, email, description: str):
        super().__init__(description=description)
        self.log = logging.getLogger(self.__class__.__name__)
        self.email = email

    @message_handler
    async def on_draft(self, message: StructuredMessage[ReportDraft], ctx: MessageContext)->None:
        self.log.info(f"ManagerAgent received tick message from {message.source}")
        payload = message.content
        # TODO: replace with actual email approval loop
        approval_data = ApproveReport(
                report_id=payload.report_id,
                approved=True,
                comments="Looks good!"
            )
        approval_message = StructuredMessage[ApproveReport](
                content=approval_data,
                source="manager_bot_agent"
            )
        #approval_topic_id = DefaultTopicId(source="approval_updates")
        await self.publish_message(message=approval_message, topic_id=STOCK_UPDATE_TOPIC)
        self.log.info(f"Published message draft report to topic {STOCK_UPDATE_TOPIC.type}")
        print(f"Published message draft report to topic {STOCK_UPDATE_TOPIC.type}")