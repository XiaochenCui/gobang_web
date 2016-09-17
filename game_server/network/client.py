import re

from cxctools.string import to_bytes, to_str
from twisted.protocols import basic
from twisted.internet import protocol, stdio
from twisted.python import log
from twisted.internet import reactor, error

from game_server.game import Game
from game_server.network.protocol import JsonReceiver


class UserInputProtocol(basic.LineReceiver):
    from os import linesep as delimiter  # @UnusedImport

    delimiter = to_bytes(delimiter)

    def __init__(self, callback):
        self.callback = callback

    def lineReceived(self, line):
        self.callback(line)


class GameClientProtocol(JsonReceiver):
    def __init__(self):
        self.game = Game()
        self.side = None

    def connectionMade(self):
        stdio.StandardIO(
            UserInputProtocol(self.user_input_received))  # 连接成功后注册UserInputProtocol，用UserInputProtocol处理用户的输入。
        self.out("Connect to server!")

    def receive_command(self, command, **params):
        commands = {
            'awaiting opponent': self.client_awaiting_opponent,
            'started': self.client_started,
            'move': self.client_make_move,
            'error': self.error_from_server,
            'opponent disconnected': self.opponent_connection_lost
        }

        if command not in commands:
            self.debug("Invalid command received: {0}".format(command))
            return

        try:
            commands[command](**params)
        except TypeError as e:
            log.msg('invalid params: {0}'.format(params))

    def client_awaiting_opponent(self):
        self.out('Waiting for the opponent...')

    def client_started(self, side):
        self.side = side
        self.out("Game started, you're playing with {0}".format(side))
        self.print_next_turn_message()

    def print_next_turn_message(self):
        if self.game.current_player == self.side:
            self.out("It's your turn now")
        else:
            self.out("It's your opponent's turn now")

    def client_make_move(self, row, col, winner=None):
        self.game.make_move(int(row), int(col))
        self.game.print_board()
        if not winner:
            self.print_next_turn_message()
        else:
            if winner == self.side:
                self.out('You win!')
            else:
                self.out('you lost!')
            self.exit_game()

    def error_from_server(self, **kwargs):
        self.out(kwargs)

    def user_input_received(self, string):
        """
        处理用户输入。

        :param string:
        :type string: bytes
        """
        # Shorthand for "move" command
        string = to_str(string)

        commands = {
            'move': self.send_make_move
        }

        match = re.match('^\s*(\d+)\s+(\d+)\s*$', string)
        if match:
            command = 'move'
            params = match.groups()
        else:
            params = filter(len, string.split(' '))
            command, params = params[0], params[1:]

        if command not in commands:
            self.out('invaild command: {}'.format(command))
            return

        try:
            commands[command](*params)
        except TypeError as e:
            raise TabError("Invalid command parameters: {0}".format(e))

    def send_command(self, command, **params):
        self.send_object(command=command, **params)

    def send_make_move(self, row, col):
        self.send_object(command='move', row=row, col=col)

    def out(self, *messages):
        for m in messages:
            print(m)

    def debug(self, *message):
        self.out(*message)

    def exit_game(self):
        self.out("Disconnecting...")
        self.transport.loseConnection()

    def opponent_connection_lost(self):
        self.out('opponent connection lost...')
        self.exit_game()

    @property
    def peer(self):
        return self.transport.getPeer()


class GameClientFactory(protocol.ClientFactory):
    protocol = GameClientProtocol

    def startedConnecting(self, connector):
        destination = connector.getDestination()
        print("Connecting to server {0}:{1}, please wait...".format(destination.host, destination.port))

    def clientConnectionFailed(self, connector, reason):
        print(reason.getErrorMessage())
        reactor.stop()  # @UndefinedVariable

    def clientConnectionLost(self, connector, reason):
        print(reason.getErrorMessage())
        try:
            reactor.stop()  # @UndefinedVariable
        except error.ReactorNotRunning:
            pass


def run_client():
    from twisted.internet import reactor
    host, port = 'localhost', 20000
    factory = GameClientFactory()
    reactor.connectTCP(host, port, factory)  # @UndefinedVariable
    reactor.run()  # @UndefinedVariable


if __name__ == '__main__':
    run_client()
