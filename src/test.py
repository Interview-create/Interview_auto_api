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

    async def do_work(self, item):
        # 處理 item

        # ...
        result = item + '_processed'
        # 將處理結果返回給主程式
        self.results.append(result)


async def main():
    items = sorted(['plan1', 'plan2', 'plan3', 'plan4', 'plan5'])

    pool = AsyncThreadPool(poolSize=5)
    results = await pool.run(items=items, doWork=pool.do_work)
    print(results)

    print('abc')


if __name__ == "__main__":
    asyncio.run(main())
