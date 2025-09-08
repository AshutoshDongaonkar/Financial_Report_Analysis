import asyncio
from datetime import datetime
from autogen_core import SingleThreadedAgentRuntime, AgentType, default_subscription, TypeSubscription
from cosmpy.protos.cosmos.staking.v1beta1.staking_pb2 import Description

from agents import PriceFetcherAgent, AnalyzerAgent, ReportGeneratorAgent, ManagerAgent
from registered_messages import FetchTick
from autogen_core import AgentId
from autogen_core import TopicId
from autogen_agentchat.messages import StructuredMessage
from constants import STOCK_UPDATE_TOPIC
import logging
log = logging.getLogger(__name__)
#import logging
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#STOCK_UPDATE_TOPIC = TopicId(type="stock_updates", source="nse_bse_feed")
async def periodic_tick(runtime: SingleThreadedAgentRuntime, interval_seconds=15):
    while True:
        tick_payload = FetchTick(timestamp=datetime.now())
        tick_message = StructuredMessage[FetchTick](content=tick_payload, source="timer")
        await runtime.publish_message(message=tick_message, topic_id=STOCK_UPDATE_TOPIC)
        log.info(f"Published tick message to topic: {STOCK_UPDATE_TOPIC.type}")
        print(f"Published tick message to topic: {STOCK_UPDATE_TOPIC.type}")
        await asyncio.sleep(interval_seconds)

async def main():

    runtime = SingleThreadedAgentRuntime()

    # Call register_instance() on the agent *instances*
    await PriceFetcherAgent.register(runtime, "price_fetcher", lambda: PriceFetcherAgent(stock_list=["INFY", "TCS"],
                                                                                         description="Price Fetcher Agent"))
    await AnalyzerAgent.register(runtime, "analyser", lambda: AnalyzerAgent(description="Price Fetcher Agent"))
    await ReportGeneratorAgent.register(runtime, "reporter", lambda: ReportGeneratorAgent(description="Price Fetcher Agent"))
    await ManagerAgent.register(runtime, "manager", lambda: ManagerAgent(email="ashu_don@hotmail.com",description="Price Fetcher Agent"))

    # 4. Start the runtime
    runtime.start()

    # 5. Start the periodic task
    await asyncio.create_task(periodic_tick(runtime, interval_seconds=15))

    # 6. Keep the runtime alive
    await runtime.stop_when_idle()

if __name__ == "__main__":
    asyncio.run(main(), debug=True)