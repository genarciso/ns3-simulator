try:
    from ns import ns
except ModuleNotFoundError:
  raise SystemExit(
    "Error: ns3 Python module not found;"
    " Python bindings may not be enabled"
    " or your PYTHONPATH might not be properly configured"
  )

class GatewayApplication(ns.Application):
    def __init__(self, node, gatewayAddress,server1Address, server2Address, port):
        ns.Application.__init__(self)
        self.gatewayNode = node
        self.gatewayAddress = ns.Ipv4Address(str(gatewayAddress))
        self.server1Address = ns.Ipv4Address(str(server1Address))
        self.server2Address = ns.Ipv4Address(str(server2Address))
        self.gatewayToServerSocket = None
        self.clientToGatewaySocket = None
        self.port = int(port)


    def StartApplication(self):
        # Cria o socket para comunicação com entre o cliente e o gateway
        print(f"GatewayApplication: Starting application on node {self.gatewayNode.GetId()}")
        typeId = ns.TypeId.LookupByName("ns3::UdpSocketFactory")
        self.clientToGatewaySocket = ns.Socket.CreateSocket(self.gatewayNode, typeId)

        print(f"GatewayApplication: Configure socket for client <-> gateway communication on node {self.gatewayNode.GetId()}")
        localAddress = ns.InetSocketAddress(self.gatewayAddress, self.port)

        self.clientToGatewaySocket.Bind(localAddress)

        print(f"GatewayApplication: Set receive callback for client <->gateway socket on node {self.gatewayNode.GetId()}")
        self.clientToGatewaySocket.SetRecvCallback(self.HandleReadMessageFromClient)

    def HandleReadMessageFromClient(self, socket):
        packet = socket.Recv()

        print(f"GatewayApplication: Received message from client on node {self.gatewayNode.GetId()}")
        data = packet.CopyData().tobytes().decode(errors='ignore')
        print(f"GatewayApplication: Message content: {data}")

        print(f"GatewayApplication: Forwarding message to server ")
        target = self.server1Address if "Server1" in data else self.server2Address

        self.SendMessageToServer(target, packet)


    def SendMessageToServer(self, serverAddress, packet):
        print(f"GatewayApplication: Sending message to server at {serverAddress} from node {self.gatewayNode.GetId()}")
        print("GatewayApplication: Create socket for gateway-to-server communication")
        typeId = ns.TypeId.LookupByName("ns3::UdpSocketFactory")
        self.gatewayToServerSocket = ns.Socket.CreateSocket(self.gatewayNode, typeId)

        print(f"GatewayApplication: Configure socket for gateway-to-server communication on node {self.gatewayNode.GetId()}")
        destinationAddress = ns.InetSocketAddress(serverAddress, 9)
        self.gatewayToServerSocket.Connect(destinationAddress)

        print(f"GatewayApplication: Sending packet to server at {serverAddress} from node {self.gatewayNode.GetId()}")
        self.gatewayToServerSocket.Send(packet)

        print(f"GatewayApplication: Closing gateway-to-server socket on node {self.gatewayNode.GetId()}")
        self.gatewayToServerSocket.Close()

    def StopApplication(self):
        print(f"GatewayApplication: Stopping application on node {self.gatewayNode.GetId()}")
        if self.clientToGatewaySocket:
            self.clientToGatewaySocket.Close()
            self.clientToGatewaySocket = None
