try:
    from ns import ns
except ModuleNotFoundError:
  raise SystemExit(
    "Error: ns3 Python module not found;"
    " Python bindings may not be enabled"
    " or your PYTHONPATH might not be properly configured"
  )

from application_gateway import GatewayApplication

from application_client import ClientApp

all_apps = []

def main():
    # Tempo de finalização da simulação em segundos
    stopTime = 15.0

    # Cria os nós da rede
    print("Create 4 nodes")
    nodes = ns.NodeContainer()
    nodes.Create(4)

    gatewayNode = nodes.Get(1)
    clientNode = nodes.Get(0)

    # Configura o canal ponto-a-ponto entre os nós
    print("Configure point-to-point channel.")
    pointToPoint = ns.PointToPointHelper()
    pointToPoint.SetDeviceAttribute("DataRate", ns.StringValue("5Mbps"))
    pointToPoint.SetChannelAttribute("Delay", ns.StringValue("2ms"))

    # Cria os pares de nós para comunicação ponto-a-ponto
    # Instala os dispositivos ponto-a-ponto nos nós
    print("Create and Install point-to-point devices for client to gateway.")
    pairClientToGateway = ns.NodeContainer()
    pairClientToGateway.Add(nodes.Get(0))
    pairClientToGateway.Add(nodes.Get(1))

    netClientToGateway = ns.NetDeviceContainer()
    netClientToGateway = pointToPoint.Install(pairClientToGateway)

    print("Create and Install point-to-point devices for gateway to server 1.")
    pairGatewayToServer1 = ns.NodeContainer()
    pairGatewayToServer1.Add(nodes.Get(1))
    pairGatewayToServer1.Add(nodes.Get(2))

    netGatewayToServer1 = ns.NetDeviceContainer()
    netGatewayToServer1 = pointToPoint.Install(pairGatewayToServer1)

    print("Create and Install point-to-point devices for gateway to server 2.")
    pairGatewayToServer2 = ns.NodeContainer()
    pairGatewayToServer2.Add(nodes.Get(1))
    pairGatewayToServer2.Add(nodes.Get(3))

    netGatewayToServer2 = ns.NetDeviceContainer()
    netGatewayToServer2 = pointToPoint.Install(pairGatewayToServer2)

    # Instala a pilha de protocolos de rede nos nós
    print("Install Internet stack.")
    internetStack = ns.InternetStackHelper()
    internetStack.SetIpv6StackInstall(False)
    internetStack.Install(nodes)

    # Configura os endereços IP para os dispositivos ponto-a-ponto
    print("Assign IP addresses.")
    addressOfNetwork = ns.Ipv4AddressHelper()

    print("Configure links IP of client to gateway.")
    addressOfNetwork.SetBase(ns.Ipv4Address("192.168.1.0"), ns.Ipv4Mask("255.255.255.0"))
    interfaceClientToGateway = addressOfNetwork.Assign(netClientToGateway)

    print("Configure links IP of gateway to server 1.")
    addressOfNetwork.SetBase(ns.Ipv4Address("10.1.1.0"), ns.Ipv4Mask("255.255.255.0"))
    interfaceGatewayToServer1 = addressOfNetwork.Assign(netGatewayToServer1)

    print("Configure links IP of gateway to server 2.")
    addressOfNetwork.SetBase(ns.Ipv4Address("10.1.2.0"), ns.Ipv4Mask("255.255.255.0"))
    interfaceGatewayToServer2 = addressOfNetwork.Assign(netGatewayToServer2)

    print("Populate routing tables.")
    ns.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

    server1Ip = interfaceGatewayToServer1.GetAddress(1)
    server2Ip = interfaceGatewayToServer2.GetAddress(1)
    gatewayIp = interfaceClientToGateway.GetAddress(1)

    print("Create echo servers.")
    serverContainer = ns.NodeContainer()
    serverContainer.Add(nodes.Get(2))
    serverContainer.Add(nodes.Get(3))

    print("Install echo servers on server nodes.")
    echoServer = ns.UdpEchoServerHelper(9)
    appsContainer =  echoServer.Install(serverContainer)
    appsContainer.Start(ns.Seconds(0))
    appsContainer.Stop(ns.Seconds(stopTime))

    print("Create gateway application")
    gatewayApplication = GatewayApplication(gatewayNode, gatewayIp, server1Ip, server2Ip, 80)
    gatewayNode.AddApplication(gatewayApplication)
    gatewayApplication.SetStartTime(ns.Seconds(0.5))
    gatewayApplication.SetStopTime(ns.Seconds(stopTime))
    all_apps.append(gatewayApplication)

    print("Create client application")
    clientApplication = ClientApp(clientNode, gatewayIp, 80)
    clientNode.AddApplication(clientApplication)
    clientApplication.SetStartTime(ns.Seconds(0.7))
    clientApplication.SetStopTime(ns.Seconds(stopTime))
    all_apps.append(clientApplication)

    print("Enable ASCII and PCAP tracing.")
    ascii = ns.AsciiTraceHelper()
    pointToPoint.EnableAsciiAll(ascii.CreateFileStream("./scratch/gateway-client-server/minha-simulacao.tr"))
    pointToPoint.EnablePcap("./scratch/gateway-client-server/scenario1", netClientToGateway.Get(1))


    print("Run Simulation.")
    ns.Simulator.Run()
    ns.Simulator.Destroy()
    print("Simulation finished.")
    return 0

if __name__ == "__main__":
    main()
