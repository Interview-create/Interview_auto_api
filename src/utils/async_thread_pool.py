import asyncio


class AsyncThreadPool:
    def __init__(self, poolSize):
        self.poolSize = poolSize
        self.semaphore = asyncio.Semaphore(poolSize)
        self.results = []

    async def run(self, items, doWork):
        async def worker(item):
            async with self.semaphore:
                await doWork(item)

        tasks = [worker(item) for item in items]

        await asyncio.gather(*tasks)

        return self.results
