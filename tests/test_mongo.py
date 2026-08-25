import asyncio

import pytest
from conftest import client

motor = pytest.importorskip("motor")

pytestmark = pytest.mark.integration

index = client.index("mongo")


async def test_sync():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://root:root@localhost:27017", directConnection=True
    )
    db = client.test
    collection = db.test
    await collection.delete_many({})
    data = {
        "age": 18,
    }
    inserted_id = (await collection.insert_one(data)).inserted_id
    await asyncio.sleep(2)
    ret = await index.get_documents()
    assert ret.results == [
        {
            "age": 18,
            "_id": str(inserted_id),
        }
    ]
