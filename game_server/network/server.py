import random
from collections import deque

from twisted.python import log
from twisted.internet import protocol
from twisted.application import service

from game_server.game import Game, BLACK, WHITE
from game_server.network.protocol import JsonReceiver


class GameServerProtocol(JsonReceiver):
    STATE_AWAITING_OPPONENT = 1
    STATE_MAKING_MOVE = 2
    STATE_AWAITING_MOVE = 3
    STATE_FINISHED = 4

    def __init__(self):
        self.state = GameServerProtocol.STATE_AWAITING_OPPONENT
        self.game = None
        self.opponent = None

    def connectionMade(self):
        log.msg('Connection made from {0}:{1}'.format(self.peer.host, self.peer.port))
        self.send_command('awaiting opponent')

        # Find an opponent or add self to a queue
        self.factory.find_opponent(self)

    def connectionLost(self, reason):
        self.factory.player_disconnected(self)
        log.msg("Connection lost from {0}:{1}".format(self.peer.host, self.peer.port))

        if self.state != GameServerProtocol.STATE_FINISHED and self.opponent is not None:
            self.opponent.opponent_connection_lost(reason)

    def receive_command(self, command, **params):
        """
        Run command received from client.

        :param command:
        :param params:
        """
        commands = {
            'move': self.run_make_move_command
        }

        if command not in commands:
            log.msg('invalid command: {0}'.format(command))
            return

        # try:
        commands[command](**params)
        # except TypeError as e:
            # log.msg('invalid params: {0}'.format(params), exc_info=True)

    def run_make_move_command(self, row, col):
        if self.state == GameServerProtocol.STATE_MAKING_MOVE:
            try:
                self.game.make_move(int(row), int(col))
            except ValueError as e:
                log.msg('Invalid move: {}, {}'.format(row, col))
            else:
                self.make_move(row, col)
                self.opponent.make_move_from_opponent(row, col)
        else:
            self.send_error('It\'s not your turn!')

    def make_move(self, row, col):
        self._move_made(row, col, new_state=GameServerProtocol.STATE_AWAITING_MOVE)

    def make_move_from_opponent(self, row, col):
        self._move_made(row, col, new_state=GameServerProtocol.STATE_MAKING_MOVE)

    def _move_made(self, row, col, new_state):
        self.send_command(command='move', row=row, col=col, winner=int(self.game.winner))

        if self.game.finished:
            self.state = GameServerProtocol.STATE_FINISHED
        else:
            self.state = new_state

    def send_command(self, command, **params):
        self.send_object(command=command, **params)

    def send_error(self, err_msg):
        self.send_command('error', message=err_msg)

    def start_game(self, game, opponent, side):
        self.game = game
        self.opponent = opponent
        if side == BLACK:
            self.state = GameServerProtocol.STATE_MAKING_MOVE
        else:
            self.state = GameServerProtocol.STATE_AWAITING_MOVE
        self.send_command('started', side=side)

    def opponent_connection_lost(self, reason):
        self.send_command('opponent disconnected')

    @property
    def peer(self):
        return self.transport.getPeer()


class GameServerFactory(protocol.ServerFactory):
    protocol = GameServerProtocol
    queue = deque()

    def __init__(self):
        pass

    def find_opponent(self, player):
        try:
            opponent = self.queue.popleft()
        except IndexError:
            self.queue.append(player)
        else:
            game = Game()
            side1, side2 = random.choice([(BLACK, WHITE), (WHITE, BLACK)])
            player.start_game(game, opponent, side1)
            opponent.start_game(game, player, side2)

    def player_disconnected(self, player):
        try:
            self.queue.remove(player)
        except ValueError:
            pass
