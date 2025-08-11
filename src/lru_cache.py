import collections

import ulogging
from microtyping import Callable, Generic, List, Tuple, TypeVar

K = TypeVar("K")
V = TypeVar("V")

logger = ulogging.getLogger("LRUCache")

HIT_RATE_LOG_COUNT = const(1000)


class LRUCache(Generic[K, V]):

    def __init__(self, capacity: int, data_loader: Callable[[K], List[Tuple[K, V]]], name: str = ""):
        self.name = name
        self.capacity = capacity
        self.cache = collections.OrderedDict()
        self.data_loader = data_loader
        self.hits = 0
        self.reads = 0

    def get(self, key: K) -> V:
        self.reads += 1
        value = self.cache.get(key, None)
        if value:
            # Move the accessed item to the end of the OrderedDict
            del self.cache[key]
            self.cache[key] = value
            self.hits += 1
        else:
            values = self.data_loader(key)
            for k, v in values:
                self.cache[k] = v
            value = self.cache[key]

        if len(self.cache) > self.capacity:
            lru_key = next(iter(self.cache.keys()))
            del self.cache[lru_key]

        if self.reads % HIT_RATE_LOG_COUNT == 0:
            logger.info(
                "Cache [%s] hits: %s, reads: %s, hit rate: %.2f%%",
                self.name,
                self.hits,
                self.reads,
                (self.hits / self.reads) * 100,
            )
            self.reads = 0
            self.hits = 0

        return value
