from ns import ns

from scenario1_application_gateway import GatewayApplication

from scenario1_application_client import ClientApp

from ctypes import c_bool, c_int

all_apps = []

def main():
    # Tempo de finalização da simulação em segundos
    stopTime = c_int(10)

    # Cria os nós da rede
    # ns.log.info("Scenario1: Create 4 nodes")
    nodes = ns.NodeContainer()
    nodes.Create(4)

    gatewayNode = nodes.Get(1)
    clientNode = nodes.Get(0)

    # Configura o canal ponto-a-ponto entre os nós
    # ns.log.info("Scenario1:Configure point-to-point channel.")
    pointToPoint = ns.PointToPointHelper()
    pointToPoint.SetDeviceAttribute("DataRate", ns.StringValue("5Mbps"))
    pointToPoint.SetChannelAttribute("Delay", ns.StringValue("2ms"))

    # Cria os pares de nós para comunicação ponto-a-ponto
    # ns.log.info("Scenario1: Create pairs of connections.")

    # Instala os dispositivos ponto-a-ponto nos nós
    # ns.log.info("Scenario1: Install point-to-point devices.")
    pairClientToGateway = ns.NodeContainer()
    pairClientToGateway.Add(nodes.Get(0))
    pairClientToGateway.Add(nodes.Get(1))

    netClientToGateway = ns.NetDeviceContainer()
    netClientToGateway = pointToPoint.Install(pairClientToGateway)

    pairGatewayToServer1 = ns.NodeContainer()
    pairGatewayToServer1.Add(nodes.Get(1))
    pairGatewayToServer1.Add(nodes.Get(2))

    netGatewayToServer1 = ns.NetDeviceContainer()
    netGatewayToServer1 = pointToPoint.Install(pairGatewayToServer1)

    pairGatewayToServer2 = ns.NodeContainer()
    pairGatewayToServer2.Add(nodes.Get(1))
    pairGatewayToServer2.Add(nodes.Get(3))

    netGatewayToServer2 = ns.NetDeviceContainer()
    netGatewayToServer2 = pointToPoint.Install(pairGatewayToServer2)


    # Instala a pilha de protocolos de rede nos nós
    # ns.log.info("Scenario1: Install Internet stack.")
    internetStack = ns.InternetStackHelper()
    internetStack.SetIpv6StackInstall(c_bool(False))
    internetStack.Install(nodes)

    # Configura os endereços IP para os dispositivos ponto-a-ponto
    # ns.log.info("Scenario1:Assign IP addresses.")
    addressOfNetwork = ns.Ipv4AddressHelper()

    addressOfNetwork.SetBase(ns.Ipv4Address("11.1.0.0"), ns.Ipv4Mask("255.255.255.0"))
    interfaceClientToGateway = addressOfNetwork.Assign(netClientToGateway)

    addressOfNetwork.SetBase(ns.Ipv4Address("10.1.0.0"), ns.Ipv4Mask("255.255.255.0"))
    interfaceGatewayToServer1 = addressOfNetwork.Assign(netGatewayToServer1)
    interfaceGatewayToServer2 = addressOfNetwork.Assign(netGatewayToServer2)

    ns.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

    serverContainer = ns.NodeContainer()
    serverContainer.Add(nodes.Get(2))
    serverContainer.Add(nodes.Get(3))

    echoServer = ns.UdpEchoServerHelper(9)
    appsContainer =  echoServer.Install(serverContainer)
    appsContainer.Start(ns.Seconds(1.0))
    appsContainer.Stop(ns.Seconds(stopTime.value))

    gatewayApplication = GatewayApplication(gatewayNode, interfaceGatewayToServer1.GetAddress(1), interfaceGatewayToServer2.GetAddress(1))
    gatewayNode.AddApplication(gatewayApplication)
    gatewayApplication.SetStartTime(ns.Seconds(0.5))
    gatewayApplication.SetStopTime(ns.Seconds(stopTime.value))
    all_apps.append(gatewayApplication)

    clientApplication = ClientApp(clientNode, interfaceClientToGateway.GetAddress(1), 8080)
    clientNode.AddApplication(clientApplication)
    clientApplication.SetStartTime(ns.Seconds(0.5))
    clientApplication.SetStopTime(ns.Seconds(stopTime.value))
    all_apps.append(clientApplication)

    ascii = ns.AsciiTraceHelper()
    pointToPoint.EnableAsciiAll(ascii.CreateFileStream("./scratch/gateway-client-server/minha-simulacao.tr"))
    pointToPoint.EnablePcap("./scratch/gateway-client-server/scenario1.pcap", netClientToGateway.Get(1))


    print("Run Simulation.")
    ns.Simulator.Stop(ns.Seconds(stopTime.value + 1))
    ns.Simulator.Run()
    ns.Simulator.Destroy()

if __name__ == "__main__":
    main()
