import asyncio
from dotenv import load_dotenv
from agentics.agentic import DataProcessingAgentic

load_dotenv(override=True)

async def main():
    print("====== Hello from data-processing-agent! ======")
    query = input("What kind of crop disease would like to search and know about ?").strip()
    dataProcessing = DataProcessingAgentic(name="Data-Processing-Multi-Agent")
    
    if not query:
        await dataProcessing.run(query)
    else:
        await dataProcessing.run()

if __name__ == "__main__":
    asyncio.run(main())
