"""
NOTE: Copy this together with installation.py and installation_monitor.py since they depend on the definitions below.
"""
import dataclasses
import enum
import struct


class State(enum.IntEnum):
    OFF = 0
    DEMO = 1
    INTERACTIVE = 2


class Messages(enum.IntEnum):
    MSG_OFF_MODE = 0
    MSG_DEMO_MODE = 1
    MSG_INTERACTIVE_MODE = 2
    MSG_KEEP_ALIVE = 3


@dataclasses.dataclass
class Response:
    """
    Packet sent back to the `InstallationMonitor` as acknowledgement.
    """
    id: int
    state: int


MsgRspFmt = struct.Struct("2B")  # Message response packet format
