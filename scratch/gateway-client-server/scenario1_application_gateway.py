try:
    from ns import ns
except ModuleNotFoundError:
  raise SystemExit(
    "Error: ns3 Python module not found;"
    " Python bindings may not be enabled"
    " or your PYTHONPATH might not be properly configured"
  )

from ctypes import  c_int

class GatewayApplication(ns.Application):
    def __init__(self, node, server1Address, server2Address):
        ns.Application.__init__(self)
        self.gatewayNode = node
        self.server1Address = ns.Ipv4Address.ConvertFrom(server1Address)
        self.server2Address = ns.Ipv4Address.ConvertFrom(server2Address)
        self.gatewayToServerSocket = None
        self.clientToGatewaySocket = None
        self.port = 8080


    def StartApplication(self):
        # Cria os sockets para comunicação com o cliente e os servidores
        typeId = ns.TypeId.LookupByName("ns3::UdpSocketFactory")
        self.clientToGatewaySocket = ns.Socket.CreateSocket(self.gatewayNode, typeId)

        localAddress = ns.InetSocketAddress(ns.Ipv4Address.GetAny(), c_int(self.port))
        self.clientToGatewaySocket.Bind(localAddress)

        self.clientToGatewaySocket.SetRecvCallback(self.HandleReadMessageFromClient)

    def HandleReadMessageFromClient(self, socket):
        packet = socket.Recv()

        data = packet.ToString()

        # Verifique se os endereços foram configurados no setup()
        if self.server1Address is None or self.server2Address is None:
            print("Erro: Endereços dos servidores não configurados no Gateway!")
            return
        # ns.log.info("Scenario1: Gateway received message from client: " + str(data))

        if "Server1" in data:
            self.SendMessageToServer(self.server1Address, packet)
        else:
            self.SendMessageToServer(self.server2Address, packet)


    def SendMessageToServer(self, serverAddress, packet):
        typeId = ns.TypeId.LookupByName("ns3::UdpSocketFactory")
        self.gatewayToServerSocket = ns.Socket.CreateSocket(self.gatewayNode, typeId)

        self.gatewayToServerSocket.Connect(ns.InetSocketAddress(ns.Address(serverAddress), c_int(9)))
        self.gatewayToServerSocket.Send(packet)

    def StopApplication(self):
        if self.clientToGatewaySocket:
            self.clientToGatewaySocket.Close()
            self.clientToGatewaySocket = None
        if self.gatewayToServerSocket:
            self.gatewayToServerSocket.Close()
            self.gatewayToServerSocket = None
