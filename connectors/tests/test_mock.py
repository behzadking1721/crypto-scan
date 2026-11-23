import asyncio
import pytest

from connectors.mock import MockRestConnector, MockStreamConnector
from connectors.types import ConnectContext, Timeouts
from connectors.errors import TransientConnectorError, PermanentConnectorError
from uuid import uuid4


@pytest.mark.asyncio
async def test_mock_rest_lifecycle():
    c = MockRestConnector(None)
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    await c.connect(ctx)
    assert c.is_connected
    await c.connect(ctx)
    assert c.is_connected
    await c.disconnect()
    assert not c.is_connected
    await c.disconnect()
    assert not c.is_connected


@pytest.mark.asyncio
async def test_mock_rest_latest():
    c = MockRestConnector(None)
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    await c.connect(ctx)
    items = [r async for r in c.fetch_latest(None)]
    assert len(items) == 1
    assert items[0].ts_event.tzinfo is not None


@pytest.mark.asyncio
async def test_mock_rest_historical():
    c = MockRestConnector(None)
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    await c.connect(ctx)
    items = [r async for r in c.fetch_historical(None)]
    assert len(items) == 3


@pytest.mark.asyncio
async def test_mock_rest_missing_asset():
    c = MockRestConnector(None)
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    await c.connect(ctx)
    class Req:
        symbol = "NOPE"
    with pytest.raises(PermanentConnectorError):
        [r async for r in c.fetch_latest(Req())]


@pytest.mark.asyncio
async def test_mock_rest_empty():
    c = MockRestConnector(None, assets=[])
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    await c.connect(ctx)
    items = [r async for r in c.fetch_latest(None)]
    assert items == []


@pytest.mark.asyncio
async def test_mock_rest_transient():
    c = MockRestConnector(None, fail_mode="transient")
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    with pytest.raises(TransientConnectorError):
        await c.connect(ctx)


@pytest.mark.asyncio
async def test_mock_rest_permanent():
    c = MockRestConnector(None, fail_mode="permanent")
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    with pytest.raises(PermanentConnectorError):
        await c.connect(ctx)


@pytest.mark.asyncio
async def test_mock_stream():
    c = MockStreamConnector(None)
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    await c.connect(ctx)
    await c.subscribe([])
    msgs = [m async for m in c.stream(None)]
    assert len(msgs) == 3
    await c.disconnect()


@pytest.mark.asyncio
async def test_mock_stream_cancel():
    c = MockStreamConnector(None, delay=0.05, count=10)
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    await c.connect(ctx)
    async def run():
        async for _ in c.stream(None):
            await asyncio.sleep(0)
    task = asyncio.create_task(run())
    await asyncio.sleep(0.01)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await c.disconnect()
    assert not c._subs


@pytest.mark.asyncio
async def test_registry_manager_integration():
    from connectors.registry import ConnectorRegistry
    from connectors.manager import ConnectorManager
    m = ConnectorManager()
    sid = uuid4()
    m.register(sid, lambda cred: MockRestConnector(cred), None)
    assert m.get(sid) is not None
    ctx = ConnectContext(source_id=sid, base_url="http://x", environment="test", timeouts=Timeouts())
    await m.connect(sid, ctx)
    await m.disconnect(sid)


@pytest.mark.asyncio
async def test_mock_rest_historical_missing():
    c = MockRestConnector(None)
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    await c.connect(ctx)
    class Req:
        symbol = "NOPE"
    with pytest.raises(PermanentConnectorError):
        [r async for r in c.fetch_historical(Req())]


@pytest.mark.asyncio
async def test_mock_rest_historical_empty():
    c = MockRestConnector(None, assets=[])
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    await c.connect(ctx)
    items = [r async for r in c.fetch_historical(None)]
    assert items == []


@pytest.mark.asyncio
async def test_mock_stream_cancel_cleanup():
    c = MockStreamConnector(None, delay=0.01, count=5)
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    await c.connect(ctx)
    await c.subscribe([__import__("connectors.types", fromlist=["Subscription"]).Subscription(channel="t")])
    assert len(c._subs) == 1
    task = asyncio.create_task(c.stream(None).__anext__())
    await asyncio.sleep(0.05)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await c.unsubscribe([__import__("connectors.types", fromlist=["Subscription"]).Subscription(channel="t")])
    await c.disconnect()
    assert c._subs == []


@pytest.mark.asyncio
async def test_mock_rest_determinism():
    c1 = MockRestConnector(None)
    c2 = MockRestConnector(None)
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    await c1.connect(ctx)
    await c2.connect(ctx)
    a = [r.payload for r in [x async for x in c1.fetch_latest(None)]]
    b = [r.payload for r in [x async for x in c2.fetch_latest(None)]]
    assert a == b


@pytest.mark.asyncio
async def test_mock_stream_determinism():
    c1 = MockStreamConnector(None, count=3)
    c2 = MockStreamConnector(None, count=3)
    ctx = ConnectContext(source_id=uuid4(), base_url="http://x", environment="test", timeouts=Timeouts())
    await c1.connect(ctx)
    await c2.connect(ctx)
    a = [m.stream_meta.seq for m in [x async for x in c1.stream(None)]]
    b = [m.stream_meta.seq for m in [x async for x in c2.stream(None)]]
    assert a == b

