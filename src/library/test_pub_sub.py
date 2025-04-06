import queue
from typing import List
from src.library.pub_sub import PubSub


def test_pub_sub_init() -> None:
    """Test that PubSub initializes with empty subscribers and pending messages."""
    pub_sub = PubSub[int]()
    assert pub_sub._subs == []
    assert pub_sub._pending_messages == []


def test_sub_adds_observer() -> None:
    """Test that subscribing adds the observer to the subscribers list."""
    pub_sub = PubSub[str]()
    messages: List[str] = []

    def observer(value: str) -> None:
        messages.append(value)

    unsub = pub_sub.sub(observer)
    assert observer in pub_sub._subs
    assert callable(unsub)


def test_unsub_removes_observer() -> None:
    """Test that unsubscribing removes the observer from the subscribers list."""
    pub_sub = PubSub[str]()
    messages: List[str] = []

    def observer(value: str) -> None:
        messages.append(value)

    unsub = pub_sub.sub(observer)
    assert observer in pub_sub._subs

    unsub()
    assert observer not in pub_sub._subs


def test_pub_with_subscribers() -> None:
    """Test that publishing with subscribers calls each observer."""
    pub_sub = PubSub[int]()
    messages1: List[int] = []
    messages2: List[int] = []

    def observer1(value: int) -> None:
        messages1.append(value)

    def observer2(value: int) -> None:
        messages2.append(value)

    pub_sub.sub(observer1)
    pub_sub.sub(observer2)

    pub_sub.pub(42)

    assert messages1 == [42]
    assert messages2 == [42]


def test_pub_without_subscribers() -> None:
    """Test that publishing without subscribers stores messages for later delivery."""
    pub_sub = PubSub[str]()
    messages: List[str] = []

    pub_sub.pub("hello")
    pub_sub.pub("world")

    assert pub_sub._pending_messages == ["hello", "world"]

    def observer(value: str) -> None:
        messages.append(value)

    pub_sub.sub(observer)

    assert messages == ["hello", "world"]
    assert pub_sub._pending_messages == []


def test_multiple_subscriptions_same_observer() -> None:
    """Test that subscribing the same observer multiple times only adds it once."""
    pub_sub = PubSub[int]()
    messages: List[int] = []

    def observer(value: int) -> None:
        messages.append(value)

    pub_sub.sub(observer)
    pub_sub.sub(observer)  # Subscribe again with the same observer

    pub_sub.pub(42)

    assert messages == [42]  # Message should be received only once
    assert len(pub_sub._subs) == 1


def test_pub_sub_with_different_types() -> None:
    """Test PubSub with different generic types."""
    pub_sub_int = PubSub[int]()
    pub_sub_str = PubSub[str]()

    int_messages: List[int] = []
    str_messages: List[str] = []

    def int_observer(value: int) -> None:
        int_messages.append(value)

    def str_observer(value: str) -> None:
        str_messages.append(value)

    pub_sub_int.sub(int_observer)
    pub_sub_str.sub(str_observer)

    pub_sub_int.pub(42)
    pub_sub_str.pub("hello")

    assert int_messages == [42]
    assert str_messages == ["hello"]


def test_enqueue_method() -> None:
    """Test the enqueue method of PubSub."""
    pub_sub = PubSub[int]()
    q: queue.Queue[int] = queue.Queue()

    unsub = pub_sub.enqueue(q)

    pub_sub.pub(1)
    pub_sub.pub(2)
    pub_sub.pub(3)

    assert q.get() == 1
    assert q.get() == 2
    assert q.get() == 3

    unsub()

    pub_sub.pub(4)
    assert q.empty()  # No more messages should be enqueued after unsubscribing


def test_map_method() -> None:
    """Test the map method of PubSub."""
    pub_sub_int = PubSub[int]()
    pub_sub_str = pub_sub_int.map(str)

    int_messages: List[int] = []
    str_messages: List[str] = []

    def int_observer(value: int) -> None:
        int_messages.append(value)

    def str_observer(value: str) -> None:
        str_messages.append(value)

    pub_sub_int.sub(int_observer)
    pub_sub_str.sub(str_observer)

    pub_sub_int.pub(42)

    assert int_messages == [42]
    assert str_messages == ["42"]

    pub_sub_int.pub(100)

    assert int_messages == [42, 100]
    assert str_messages == ["42", "100"]
