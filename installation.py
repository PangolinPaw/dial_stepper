"""`Installation` runs on an installation raspberry pi and handles messages from the `InstallationMonitor`. Every
message from the `InstallationMonitor` is acknowledged by responding with a Response packet."""

import socketserver

from messages import State, Messages, MsgRspFmt, Response


class MessageHandler(socketserver.BaseRequestHandler):
    def handle(self):
        """
        self.request consists of a pair of data and client socket.
        self.client_address in this case would be the `InstallationMonitor`.
        The client address must be given explicitly when sending data back via sendto.
        :return:
        """
        data = self.request[0]
        socket = self.request[1]  # incoming connection
        print(f"{self.client_address[0]} wrote: {data}")

        msg = self.server.parse_packet(data)
        rsp = self.server.handle_msg(msg)

        # send response to the monitor
        socket.sendto(MsgRspFmt.pack(rsp.id, rsp.state), self.client_address)

        print(f"current_state = {self.server.current_state()}")


class Installation(socketserver.UDPServer):
    """
    Represents a physical installation in the Challenge Dyson event.

    Handles requests from the `InstallationMonitor` and responds with `Response` packet as acknowledgement.
    Can be in any one of three states -
        - OFF
        - DEMO
        - INTERACTIVE
    """
    state: State = State.DEMO

    def __init__(self, self_ip: str, port: int, id: int, init_state: State = State.DEMO):
        """
        Assigns the installation the given unique id and initializes it to the specified state.

        Must be called before using any of the methods.
        """
        super().__init__((self_ip, port), MessageHandler)
        self.id = id
        self.state = init_state

    def current_state(self):
        """
        Returns the latest possible state of the installation.
        :return:
        """
        return self.state

    def turn_off(self):
        self.state = State.OFF

    def start_demo(self):
        self.state = State.DEMO

    def ack_keep_alive(self):
        # leave the state unchanged
        pass

    def start_interactive(self):
        self.state = State.INTERACTIVE

    def parse_packet(self, pkt: bytes) -> Messages:
        k = pkt[0]
        if k == Messages.MSG_OFF_MODE:
            return Messages.MSG_OFF_MODE

        if k == Messages.MSG_DEMO_MODE:
            return Messages.MSG_DEMO_MODE

        if k == Messages.MSG_INTERACTIVE_MODE:
            return Messages.MSG_INTERACTIVE_MODE

        if k == Messages.MSG_KEEP_ALIVE:
            return Messages.MSG_KEEP_ALIVE

    def handle_msg(self, msg: Messages) -> Response:
        if msg == Messages.MSG_OFF_MODE:
            self.turn_off()
        elif msg == Messages.MSG_DEMO_MODE:
            self.start_demo()
        elif msg == Messages.MSG_INTERACTIVE_MODE:
            self.start_interactive()
        elif msg == Messages.MSG_KEEP_ALIVE:
            print("keep alive")
            self.ack_keep_alive()

        return Response(self.id, self.state)
