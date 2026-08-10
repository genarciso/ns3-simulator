from ctypes import c_bool, c_int
try:
    from ns import ns
except ModuleNotFoundError:
    raise SystemExit(
        "Error: ns3 Python module not found;"
        " Python bindings may not be enabled"
        " or your PYTHONPATH might not be properly configured"
    )


def main():
  #  Habilitar o log
  ns.LogComponentEnable("UdpEchoClientApplication", ns.LOG_LEVEL_INFO)
  ns.LogComponentEnable("UdpEchoServerApplication", ns.LOG_LEVEL_INFO)

  # Criar nós (nó cliente e nó servidor)
  nodes = ns.NodeContainer() 
  nodes.Create(2)

  # Definir o canal Wi-Fi
  wifiChannel = ns.YansWifiChannelHelper.Default()
  phy = ns.YansWifiPhyHelper()
  phy.SetChannel(wifiChannel.Create())

  # Configurar a interface Wi-Fi
  wifi = ns.WifiHelper()
  wifi.SetRemoteStationManager("ns3::MinstrelHtWifiManager");

  # Configurar a camada MAC (gerenciamento de acesso ao meio)
  mac = ns.WifiMacHelper()
  ssid = ns.Ssid("ns-3-ssid") 
  mac.SetType("ns3::StaWifiMac", "Ssid", ns.SsidValue(ssid), "ActiveProbing", ns.BooleanValue(False))

  # Instalar no primeiro nó (estação)
  stationDevice = ns.NetDeviceContainer()
  stationDevice = wifi.Install(phy, mac, nodes.Get(0));

  # Configurar o segundo nó como ponto de acesso (AP)
  mac.SetType("ns3::ApWifiMac", "Ssid", ns.SsidValue(ssid));

  # Instalar o dispositivo de rede no AP
  apDevice = ns.NetDeviceContainer()
  apDevice = wifi.Install(phy, mac, nodes.Get(1));

  # Configurar mobilidade
  mobility = ns.MobilityHelper()
  mobility.SetPositionAllocator("ns3::GridPositionAllocator",
    "MinX",
    ns.DoubleValue(0.0),
    "MinY",
    ns.DoubleValue(0.0),
    "DeltaX",
    ns.DoubleValue(5.0),
    "DeltaY",
    ns.DoubleValue(10.0),
    "GridWidth",
    ns.UintegerValue(3),
    "LayoutType",
    ns.StringValue("RowFirst"))

  mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
  mobility.Install(nodes)

  # Instalar a pilha de protocolos de Internet (TCP/IP)
  stack = ns.InternetStackHelper()
  stack.Install(nodes)
  
  # Atribuir endereços IP
  address = ns.Ipv4AddressHelper()
  address.SetBase(ns.Ipv4Address("192.168.1.0"), ns.Ipv4Mask("255.255.255.0"))  
  stationInterface = address.Assign(stationDevice)

  apInterface = address.Assign(apDevice)

  # Configurar o servidor UDP no segundo nó (AP)
  echoServer = ns.UdpEchoServerHelper(9)
  serverApp = echoServer.Install(nodes.Get(1))
  serverApp.Start(ns.Seconds(1))  # Tempo de início do servidor
  serverApp.Stop(ns.Seconds(10))  # Tempo de parada do servidor

  # Configurar o cliente UDP no primeiro nó (estação)
  echoClient = ns.UdpEchoClientHelper(apInterface.GetAddress(0).ConvertTo(), 9)
  echoClient.SetAttribute("MaxPackets", ns.UintegerValue(0))
  echoClient.SetAttribute("Interval", ns.TimeValue(ns.Seconds(0.1)))
  echoClient.SetAttribute("PacketSize", ns.UintegerValue(1024))

  clientApp = echoClient.Install(nodes.Get(0))
  clientApp.Start(ns.Seconds(2.0)) # Tempo de início do cliente
  clientApp.Stop(ns.Seconds(9.0))  # Tempo de parada do cliente

  # Habilitar a captura de pacotes
  # Troque o caminho para o diretório onde deseja salvar o arquivo de captura
  phy.EnablePcap("./scratch/tests/wireless-client-server-by-python", apDevice.Get(0));

  # Rodar a simulação
  ns.Simulator.Stop(ns.Seconds(10.0));
  ns.Simulator.Run();
  ns.Simulator.Destroy();

  return 0

if __name__ == "__main__":
    main()
