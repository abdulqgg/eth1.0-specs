"""
Ethereum Virtual Machine (EVM) Logging Instructions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. contents:: Table of Contents
    :backlinks: none
    :local:

Introduction
------------

Implementations of the EVM logging instructions.
"""
from functools import partial

from ethereum.base_types import Uint

from ...eth_types import Log
from .. import Evm
from ..gas import (
    GAS_LOG,
    GAS_LOG_DATA,
    GAS_LOG_TOPIC,
    calculate_gas_extend_memory,
    subtract_gas,
)
from ..memory import extend_memory, memory_read_bytes
from ..stack import pop


def log_n(evm: Evm, num_topics: int) -> None:
    """
    Appends a log entry, having `num_topics` topics, to the evm logs.

    This will also expand the memory if the data (required by the log entry)
    corresponding to the memory is not accessible.

    Parameters
    ----------
    evm :
        The current EVM frame.
    num_topics :
        The number of topics to be included in the log entry.

    Raises
    ------
    StackUnderflowError
        If `len(stack)` is less than `2 + num_topics`.
    """
    # Converting memory_start_index to Uint as memory_start_index + size - 1
    # can overflow U256.
    memory_start_index = Uint(pop(evm.stack))
    size = pop(evm.stack)

    gas_cost = (
        GAS_LOG
        + (GAS_LOG_DATA * size)
        + (GAS_LOG_TOPIC * num_topics)
        + calculate_gas_extend_memory(evm.memory, memory_start_index, size)
    )
    evm.gas_left = subtract_gas(evm.gas_left, gas_cost)

    extend_memory(evm.memory, memory_start_index, size)

    log_entry = Log(
        address=evm.current,
        topics=[],
        data=memory_read_bytes(evm.memory, memory_start_index, size),
    )

    for _ in range(num_topics):
        topic = pop(evm.stack).to_be_bytes32()
        log_entry.topics.append(topic)

    evm.logs.append(log_entry)


log0 = partial(log_n, num_topics=0)
log1 = partial(log_n, num_topics=1)
log2 = partial(log_n, num_topics=2)
log3 = partial(log_n, num_topics=3)
log4 = partial(log_n, num_topics=4)
