try:
    from ns import ns
except ModuleNotFoundError:
  raise SystemExit(
    "Error: ns3 Python module not found;"
    " Python bindings may not be enabled"
    " or your PYTHONPATH might not be properly configured"
  )

from ctypes import c_int

class ClientApp(ns.Application):
    def __init__(self, node, gatewayAddress, port):
        ns.Application.__init__(self)
        self.clientNode = node
        self.gatewayAddress = ns.Ipv4Address.ConvertFrom(gatewayAddress)
        self.port = port
        self.clientSocket = None

    def StartApplication(self):
        tid = ns.TypeId.LookupByName("ns3::UdpSocketFactory")
        self.clientSocket = ns.Socket.CreateSocket(self.clientNode, tid)
        self.clientSocket.Connect(ns.InetSocketAddress(ns.Address(self.gatewayAddress), c_int(self.port)))

        # Agenda envios variando o servidor de destino no payload
        ns.Simulator.Schedule(ns.Seconds(2.0), self.SendRequest, "Server1: Ola!")
        ns.Simulator.Schedule(ns.Seconds(5.0), self.SendRequest, "Server2: Requisicao nova")

    def SendRequest(self, message):
        packet = ns.Packet(message.encode())
        self.clientSocket.Send(packet)
        print(f"Cliente: Enviando '{message}' para o Gateway")

    def StopApplication(self):
        if self.clientSocket:
            self.clientSocket.Close()
            self.clientSocket = None
