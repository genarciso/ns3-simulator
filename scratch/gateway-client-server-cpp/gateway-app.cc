#include "gateway-app.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("GatewayApplication");

GatewayApp::GatewayApp()
    : internalSocket(0),
      port(0)
{
}

GatewayApp::~GatewayApp()
{
    this->internalSocket = 0;
}

void
GatewayApp::Setup(Ipv4Address server1Ip, Ipv4Address server2Ip, uint16_t port)
{
    this->server1Addr = server1Ip;
    this->server2Addr = server2Ip;
    this->port = port;
}

void
GatewayApp::StartApplication(void)
{
    NS_LOG_UNCOND("Gateway Application: Starting application on node " << GetNode()->GetId());
    TypeId tid = TypeId::LookupByName("ns3::UdpSocketFactory");
    this->internalSocket = Socket::CreateSocket(GetNode(), tid);

    // Bind na porta configurada para ouvir o cliente
    NS_LOG_UNCOND(
        "Gateway Application: Configure socket for client <-> gateway communication on node "
        << GetNode()->GetId());
    this->internalSocket->Bind(InetSocketAddress(Ipv4Address::GetAny(), port));
    this->internalSocket->SetRecvCallback(MakeCallback(&GatewayApp::HandleRead, this));
}

void
GatewayApp::HandleRead(Ptr<Socket> socket)
{
    NS_LOG_UNCOND("Gateway Application: Received message from client on node "
                  << GetNode()->GetId());
    Ptr<Packet> packet = socket->Recv();

    // Extração do conteúdo do pacote para decisão de rota
    uint8_t* buffer = new uint8_t[packet->GetSize()];
    packet->CopyData(buffer, packet->GetSize());

    std::string data(reinterpret_cast<char*>(buffer), packet->GetSize());
    delete[] buffer;

    NS_LOG_UNCOND("Gateway Application: Message content: " << data);

    Ipv4Address target = ("Server1" == data.substr(0, 7)) ? server1Addr : server2Addr;

    NS_LOG_UNCOND("Gateway Application: Forwarding message to server " << target);
    NS_LOG_UNCOND("Gateway Application: Forwarding to " << target << " in "
                                                        << Simulator::Now().GetSeconds() << "s");
    ForwardPacket(packet, target);
}

void
GatewayApp::ForwardPacket(Ptr<Packet> packet, Ipv4Address target)
{
    NS_LOG_UNCOND("Gateway Application: Sending message to server at " << target << " from node "
                                                                       << GetNode()->GetId());
    NS_LOG_UNCOND("Gateway Application: Create socket for gateway-to-server communication");
    TypeId tid = TypeId::LookupByName("ns3::UdpSocketFactory");
    Ptr<Socket> sendSocket = Socket::CreateSocket(GetNode(), tid);

    NS_LOG_UNCOND(
        "Gateway Application: Configure socket for gateway-to-server communication on node "
        << GetNode()->GetId());
    sendSocket->Connect(InetSocketAddress(target, 9));

    NS_LOG_UNCOND("Gateway Application: Sending packet to server at " << target << " from node "
                                                                      << GetNode()->GetId());
    sendSocket->Send(packet);

    NS_LOG_UNCOND("Gateway Application: Closing gateway-to-server socket on node "
                  << GetNode()->GetId());
    sendSocket->Close();
}

void
GatewayApp::StopApplication(void)
{
    if (this->internalSocket)
    {
        NS_LOG_UNCOND("Gateway Application: Stopping application on node " << GetNode()->GetId());
        internalSocket->Close();
    }
}
