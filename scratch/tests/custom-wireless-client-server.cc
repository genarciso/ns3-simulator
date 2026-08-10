#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/network-module.h"
#include "ns3/ssid.h"
#include "ns3/wifi-module.h"
#include "ns3/yans-wifi-helper.h"

using namespace ns3;

int
main(int argc, char* argv[])
{
    // Habilitar o log
    LogComponentEnable("UdpEchoClientApplication", LOG_LEVEL_INFO);
    LogComponentEnable("UdpEchoServerApplication", LOG_LEVEL_INFO);

    // Criar nós (nó cliente e nó servidor)
    NodeContainer nodes;
    nodes.Create(2);

    // Definir o canal Wi-Fi
    YansWifiChannelHelper wifiChannel = YansWifiChannelHelper::Default();
    YansWifiPhyHelper phy;
    phy.SetChannel(wifiChannel.Create());

    // Configurar a interface Wi-Fi
    WifiHelper wifi;
    wifi.SetRemoteStationManager("ns3::MinstrelHtWifiManager");

    // Configurar a camada MAC (gerenciamento de acesso ao meio)
    WifiMacHelper mac;
    Ssid ssid = Ssid("ns-3-ssid");
    mac.SetType("ns3::StaWifiMac", "Ssid", SsidValue(ssid), "ActiveProbing", BooleanValue(false));

    // Instalar no primeiro nó (estação)
    NetDeviceContainer stationDevice;
    stationDevice = wifi.Install(phy, mac, nodes.Get(0));

    // Configurar o segundo nó como ponto de acesso (AP)
    mac.SetType("ns3::ApWifiMac", "Ssid", SsidValue(ssid));

    // Instalar o dispositivo de rede no AP
    NetDeviceContainer apDevice;
    apDevice = wifi.Install(phy, mac, nodes.Get(1));

    // Configurar mobilidade
    MobilityHelper mobility;
    mobility.SetPositionAllocator("ns3::GridPositionAllocator",
                                  "MinX",
                                  DoubleValue(0.0),
                                  "MinY",
                                  DoubleValue(0.0),
                                  "DeltaX",
                                  DoubleValue(5.0),
                                  "DeltaY",
                                  DoubleValue(10.0),
                                  "GridWidth",
                                  UintegerValue(3),
                                  "LayoutType",
                                  StringValue("RowFirst"));

    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(nodes);

    // Instalar a pilha de protocolos de Internet (TCP/IP)
    InternetStackHelper stack;
    stack.Install(nodes);

    // Atribuir endereços IP
    Ipv4AddressHelper address;
    address.SetBase("192.168.1.0", "255.255.255.0");
    Ipv4InterfaceContainer stationInterface;
    stationInterface = address.Assign(stationDevice);

    Ipv4InterfaceContainer apInterface;
    apInterface = address.Assign(apDevice);

    // Configurar o servidor UDP no segundo nó (AP)
    UdpEchoServerHelper echoServer(9);
    ApplicationContainer serverApp = echoServer.Install(nodes.Get(1));
    serverApp.Start(Seconds(1.0)); // Tempo de início do servidor
    serverApp.Stop(Seconds(10.0)); // Tempo de parada do servidor

    // Configurar o cliente UDP no primeiro nó (estação)
    UdpEchoClientHelper echoClient(apInterface.GetAddress(0), 9);
    echoClient.SetAttribute("MaxPackets", UintegerValue(0));
    echoClient.SetAttribute("Interval", TimeValue(Seconds(0.1)));
    echoClient.SetAttribute("PacketSize", UintegerValue(1024));

    ApplicationContainer clientApp = echoClient.Install(nodes.Get(0));
    clientApp.Start(Seconds(2.0)); // Tempo de início do cliente
    clientApp.Stop(Seconds(9.0));  // Tempo de parada do cliente

    // Habilitar a captura de pacotes
    // Troque o caminho para o diretório onde deseja salvar o arquivo de captura
    phy.EnablePcap("./scratch/tests/wireless-client-server", apDevice.Get(0));

    // Rodar a simulação
    Simulator::Stop(Seconds(10.0));
    Simulator::Run();
    Simulator::Destroy();

    return 0;
}
