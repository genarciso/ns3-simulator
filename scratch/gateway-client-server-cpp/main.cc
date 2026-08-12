#include "client-app.h"
#include "gateway-app.h"

#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("GatewaySimulation");

int
main(int argc, char* argv[])
{
    // Cria os nós da rede
    NS_LOG_UNCOND("Create 4 nodes");
    NodeContainer nodes;
    nodes.Create(4);

    Ptr<Node> gatewayNode = nodes.Get(1);
    Ptr<Node> clientNode = nodes.Get(0);

    // Configura o canal ponto-a-ponto entre os nós
    NS_LOG_UNCOND("Configure point-to-point channel.");
    PointToPointHelper pointToPoint;
    pointToPoint.SetDeviceAttribute("DataRate", StringValue("5Mbps"));
    pointToPoint.SetChannelAttribute("Delay", StringValue("2ms"));

    // Instala os dispositivos ponto-a-ponto nos nós
    NS_LOG_UNCOND("Create and Install point-to-point devices for client to gateway.");
    NetDeviceContainer pairClientToGateway = pointToPoint.Install(clientNode, gatewayNode);

    NS_LOG_UNCOND("Create and Install point-to-point devices for gateway to server 1.");
    NetDeviceContainer pairGatewayToServer1 = pointToPoint.Install(gatewayNode, nodes.Get(2));

    NS_LOG_UNCOND("Create and Install point-to-point devices for gateway to server 2.");
    NetDeviceContainer pairGatewayToServer2 = pointToPoint.Install(gatewayNode, nodes.Get(3));

    // Instala a pilha de protocolos de rede nos nós
    NS_LOG_UNCOND("Install Internet stack.");
    InternetStackHelper internetStack;
    internetStack.SetIpv6StackInstall(false);
    internetStack.Install(nodes);

    // Configura os endereços IP para os dispositivos ponto-a-ponto
    Ipv4AddressHelper address;

    NS_LOG_UNCOND("Configure links IP of client to gateway.");
    address.SetBase("192.168.1.0", "255.255.255.0");
    Ipv4InterfaceContainer interfaceClientToGateway = address.Assign(pairClientToGateway);

    NS_LOG_UNCOND("Configure links IP of gateway to server 1.");
    address.SetBase("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer interfaceGatewayToServer1 = address.Assign(pairGatewayToServer1);

    NS_LOG_UNCOND("Configure links IP of gateway to server 2.");
    address.SetBase("10.1.2.0", "255.255.255.0");
    Ipv4InterfaceContainer interfaceGatewayToServer2 = address.Assign(pairGatewayToServer2);

    NS_LOG_UNCOND("Populate routing tables.");
    Ipv4GlobalRoutingHelper::PopulateRoutingTables();

    uint16_t port = 8080;
    Ipv4Address server1Ip = interfaceGatewayToServer1.GetAddress(1);
    Ipv4Address server2Ip = interfaceGatewayToServer2.GetAddress(1);
    Ipv4Address gatewayIp = interfaceClientToGateway.GetAddress(1);

    // Servidores de Eco (Nós 2 e 3)
    UdpEchoServerHelper echoServer(9);
    NS_LOG_UNCOND("Create and Install echo servers on server nodes.");
    ApplicationContainer serversApps =
        echoServer.Install(NodeContainer(nodes.Get(2), nodes.Get(3)));
    serversApps.Start(Seconds(1.0));
    serversApps.Stop(Seconds(10.0));

    // Gateway (Nó 1)
    NS_LOG_UNCOND("Configure gateway application.");
    Ptr<GatewayApp> gatewayApplication = CreateObject<GatewayApp>();
    gatewayApplication->Setup(server1Ip, server2Ip, port);
    nodes.Get(1)->AddApplication(gatewayApplication);
    gatewayApplication->SetStartTime(Seconds(1.0));
    gatewayApplication->SetStopTime(Seconds(10.0));

    // Cliente (Nó 0)
    NS_LOG_UNCOND("Configure client application.");
    Ptr<ClientApp> clientApplication = CreateObject<ClientApp>();
    clientApplication->Setup(gatewayIp, port);
    nodes.Get(0)->AddApplication(clientApplication);
    clientApplication->SetStartTime(Seconds(1.5));
    clientApplication->SetStopTime(Seconds(10.0));

    NS_LOG_UNCOND("Enable ASCII and PCAP tracing.");
    AsciiTraceHelper ascii;
    pointToPoint.EnableAsciiAll(
        ascii.CreateFileStream("./scratch/gateway-client-server-cpp/simulation-gateway.tr"));
    pointToPoint.EnablePcapAll("./scratch/gateway-client-server-cpp/simulation-gateway");

    NS_LOG_UNCOND("Run Simulation.");
    Simulator::Run();
    Simulator::Destroy();
    NS_LOG_UNCOND("Simulation finished.");
    return 0;
}
