from twisted.application import internet, service
from game_server.network.server import GameServerProtocol, GameServerFactory

port = 20000
interface = 'localhost'

top_service = service.MultiService()

factory = GameServerFactory()
tcp_service = internet.TCPServer(port, factory, interface=interface)
tcp_service.setServiceParent(top_service)

application = service.Application("twisted-game-server")

top_service.setServiceParent(application)
