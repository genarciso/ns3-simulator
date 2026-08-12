try:
    from ns import ns
except ModuleNotFoundError:
  raise SystemExit(
    "Error: ns3 Python module not found;"
    " Python bindings may not be enabled"
    " or your PYTHONPATH might not be properly configured"
  )

class ClientApp(ns.Application):
    def __init__(self, node, gatewayAddress, port):
        ns.Application.__init__(self)
        self.clientNode = node
        self.gatewayAddress = ns.Ipv4Address(str(gatewayAddress))
        self.port = int(port)
        self.clientSocket = None


    def StartApplication(self):
        # Cria o socket para comunicação com entre o cliente e o gateway
        print(f"ClientApp: Starting application on node {self.clientNode.GetId()}")
        typeId = ns.TypeId.LookupByName("ns3::UdpSocketFactory")
        self.clientSocket = ns.Socket.CreateSocket(self.clientNode, typeId)

        print(f"ClientApp: Configure socket for client-to-gateway communication on node {self.clientNode.GetId()}")
        gatewaySocketAddress = ns.InetSocketAddress(self.gatewayAddress, self.port)
        self.clientSocket.Connect(gatewaySocketAddress)

        # Agenda envios variando o servidor de destino no payload
        print("ClientApp: Scheduled message to Server1 at 2 seconds")
        ns.Simulator.Schedule(ns.Seconds(2.0), self.SendRequest, "Server1: Ola!")

        print("ClientApp: Scheduled message to Server2 at 5 seconds")
        ns.Simulator.Schedule(ns.Seconds(5.0), self.SendRequest, "Server2: Requisição nova")

    def SendRequest(self, message):
        if self.clientSocket:
            packet = ns.Packet(message.encode())
            self.clientSocket.Send(packet)
            print(f"ClientApp: Sent '{message}' to gateway")

    def StopApplication(self):
        print(f"ClientApp: Stopping application on node {self.clientNode.GetId()}")
        if self.clientSocket:
            self.clientSocket.Close()
            self.clientSocket = None
