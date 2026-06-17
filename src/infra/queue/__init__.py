from arq.connections import ArqRedis


async def create_redis_pool(redis_url: str) -> ArqRedis:
    return await ArqRedis.from_url(redis_url)


async def close_redis_pool(pool: ArqRedis) -> None:
    await pool.close()
