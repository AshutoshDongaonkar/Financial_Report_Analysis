import asyncio
#import random
# Autogen Core
from datetime import datetime
from pydantic import Field
from autogen_core import SingleThreadedAgentRuntime, TypeSubscription, default_subscription
from autogen_core import TopicId
from agents import PriceFetcherAgent, AnalyzerAgent, ReportAgent
from registered_messages import StockPriceUpdate, ArbitrageSignal, DraftReport, ApproveReport, FetchTick
#from autogen_core.runtime import AgentRuntime, SingleThreadedAgentRuntime
#from autogen_core.subscriptions import Subscription, TypeSubscription
#from autogen_agentchat.agents import RoutedAgent
#from autogen_agentchat.agents import RoutedAgent

async def main():
    runtime = SingleThreadedAgentRuntime()

    stock_list = ["TCS", "INFY", "HDFCBANK"]

    # Register agents
    await PriceFetcherAgent.register(
        runtime, "fetcher",
        factory=lambda: PriceFetcherAgent(stock_list),
        #subscriptions = lambda: [default_subscription(TypeSubscription(FetchTick))],
    )
    await AnalyzerAgent.register(
        runtime, "analyzer",
        factory=lambda: AnalyzerAgent(),
        #subscriptions = lambda: [default_subscription(TypeSubscription(StockPriceUpdate))]
    )
    await ReportAgent.register(
        runtime, "reporter",
        factory=lambda: ReportAgent(),
        #subscriptions=lambda: [
            #default_subscription(TypeSubscription(ArbitrageSignal)),
            #default_subscription(TypeSubscription(ApproveReport)),
        #]
    )

    runtime.start()

    def get_iso_timestamp_str():
        """Returns the current time formatted as an ISO 8601 string."""
        return datetime.now().isoformat()
    # Create and run the periodic message task
    async def periodic_fetch(runtime: SingleThreadedAgentRuntime):
        fetcher_topic_id = TopicId(type="price-fetcher", source="")
        while True:
            # Create a FetchTick message
            tick_message = FetchTick(timestamp=Field(default_factory=get_iso_timestamp_str))
            # Publish the message to the "fetcher" agent's topic
            await runtime.publish_message(tick_message, topic_id=fetcher_topic_id)
            # Wait for 5 minutes (300 seconds)
            await asyncio.sleep(300)

    # Start the periodic task in the background
        # Pass the runtime to the periodic task
    periodic_task = asyncio.create_task(periodic_fetch(runtime))

    await runtime.stop_when_idle()

if __name__ == "__main__":
    asyncio.run(main())