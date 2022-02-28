from bevy.app.agents import Agent, hook
import pytest


def test_hook():
    result = set()

    class TestAgent(Agent):
        @hook("test_hook")
        def test_hook_callback(self, msg):
            result.add(msg)

    agent = TestAgent()
    agent.dispatch_to_hook("test_hook", "testing")
    assert result == {"testing"}


@pytest.mark.asyncio
async def test_async_hook():
    result = set()

    class TestAgent(Agent):
        @hook("test_hook")
        async def test_hook_callback(self, msg):
            result.add(msg)

    agent = TestAgent()
    await agent.dispatch_to_hook("test_hook", "testing")
    assert result == {"testing"}


@pytest.mark.asyncio
async def test_multicolor_hooks():
    result = set()

    class TestAgent(Agent):
        @hook("test_hook")
        async def test_hook_async_callback(self, msg):
            result.add(f"B {msg}")

        @hook("test_hook")
        def test_hook_callback(self, msg):
            result.add(f"A {msg}")

    agent = TestAgent()
    await agent.dispatch_to_hook("test_hook", "testing")
    assert result == {"A testing", "B testing"}


def test_hook_repository_isolation():
    result = set()

    class TestAgentA(Agent):
        @hook("test_hook")
        def test_hook_async_callback(self, msg):
            result.add(f"A {msg}")

    class TestAgentB(Agent):
        @hook("test_hook")
        def test_hook_async_callback(self, msg):
            result.add(f"B {msg}")

    agent = TestAgentA()
    agent.dispatch_to_hook("test_hook", "testing")
    assert result == {"A testing"}


def test_hook_inheritance():
    class TestAgentA(Agent):
        @hook("test_hook")
        def test_hook_async_callback(self, msg):
            result.add(f"A {msg}")

        @hook("test_hook")
        def test_hook_async_callback_c(self, msg):
            result.add(f"D {msg}")

    class TestAgentB(TestAgentA):
        @hook("test_hook")
        def test_hook_async_callback(self, msg):
            result.add(f"B {msg}")

    class TestAgentBB(TestAgentB):
        @hook("test_hook")
        def test_hook_async_callback(self, msg):
            result.add(f"BB {msg}")

        @hook("test_hook")
        def test_hook_async_callback_bbb(self, msg):
            result.add(f"BBB {msg}")

    class TestAgentC(TestAgentA):
        @hook("test_hook")
        def test_hook_async_callback(self, msg):
            result.add(f"C {msg}")

    result = set()
    agent = TestAgentB()
    agent.dispatch_to_hook("test_hook", "testing")
    assert result == {"B testing", "D testing"}

    result = set()
    agent = TestAgentA()
    agent.dispatch_to_hook("test_hook", "testing")
    assert result == {"A testing", "D testing"}

    result = set()
    agent = TestAgentBB()
    agent.dispatch_to_hook("test_hook", "testing")
    assert result == {"BB testing", "BBB testing", "D testing"}
