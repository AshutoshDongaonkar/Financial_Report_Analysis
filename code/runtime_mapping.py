import asyncio
from datetime import datetime
from autogen_core import SingleThreadedAgentRuntime, AgentType, default_subscription
from agents import PriceFetcherAgent, AnalyzerAgent, ReportGeneratorAgent, ManagerAgent
from registered_messages import FetchTick
from autogen_core import AgentId
from autogen_core import TopicId
from autogen_agentchat.messages import StructuredMessage
from constants import STOCK_UPDATE_TOPIC

#STOCK_UPDATE_TOPIC = TopicId(type="stock_updates", source="nse_bse_feed")
async def periodic_tick(runtime: SingleThreadedAgentRuntime, interval_seconds=300):
    while True:
        tick_payload = FetchTick(timestamp=datetime.now())
        tick_message = StructuredMessage[FetchTick](content=tick_payload, source="timer")
        await runtime.publish_message(message=tick_message, topic_id=STOCK_UPDATE_TOPIC)
        await asyncio.sleep(interval_seconds)

async def main():
    # Register PriceFetcherAgent
    await PriceFetcherAgent.register(
        AgentType("price_fetcher"),
        lambda agent_id: PriceFetcherAgent(name=f"fetcher_{agent_id.key}", stock_list=["INFY", "TCS"])
    )

    # Register AnalyzerAgent
    await AnalyzerAgent.register(
        AgentType("arbitrage_analyzer"),
        lambda agent_id: AnalyzerAgent(name=f"analyzer_{agent_id.key}")
    )

    # Register ReportGeneratorAgent
    await ReportGeneratorAgent.register(
        AgentType("reporting_agent"),
        lambda agent_id: ReportGeneratorAgent(name=f"reporter_{agent_id.key}")
    )

    # Register ManagerAgent
    await ManagerAgent.register(
        AgentType("human_approver"),
        lambda agent_id: ManagerAgent(name=f"manager_{agent_id.key}", email="ashu_don@hotmail.com")
    )
    runtime = SingleThreadedAgentRuntime()
'''
    fetcher = PriceFetcherAgent(["INFY", "TCS"])
    analyzer = AnalyzerAgent()
    reporter = ReportGeneratorAgent()
    manager = ManagerAgent("ashu_don@hotmail.com")

    # Create AgentId objects
    price_fetcher_id = AgentId(type="price_fetcher", key="default")
    analyzer_id = AgentId(type="arbitrage_analyzer", key="default")
    reporter_id = AgentId(type="reporting_agent", key="default")
    manager_id = AgentId(type="human_approver", key="default")

    # Register agents
    await runtime.register_agent_instance(fetcher, agent_id=price_fetcher_id)
    await runtime.register_agent_instance(analyzer, agent_id=analyzer_id)
    await runtime.register_agent_instance(reporter, agent_id=reporter_id)
    await runtime.register_agent_instance(manager, agent_id=manager_id)
'''

     # Start runtime
    runtime.start()
    # Start periodic tick
    await asyncio.create_task(periodic_tick(runtime, interval_seconds=15))

    await runtime.stop_when_idle()


if __name__ == "__main__":
    asyncio.run(main(), debug=True)