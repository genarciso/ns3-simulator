#include "client-app.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("ClientApplication");

ClientApp::ClientApp()
    : internalSocket(0),
      port(0)
{
}

ClientApp::~ClientApp()
{
    this->internalSocket = 0;
}

void
ClientApp::Setup(Ipv4Address gatewayAddr, uint16_t port)
{
    this->gatewayAddr = gatewayAddr;
    this->port = port;
}

void
ClientApp::StartApplication(void)
{
    NS_LOG_UNCOND("Client Application: Starting application on node " << GetNode()->GetId());
    TypeId tid = TypeId::LookupByName("ns3::UdpSocketFactory");
    this->internalSocket = Socket::CreateSocket(GetNode(), tid);

    NS_LOG_UNCOND(
        "Client Application: Configure socket for client <-> gateway communication on node "
        << GetNode()->GetId());
    this->internalSocket->Connect(InetSocketAddress(this->gatewayAddr, this->port));

    // Agenda envios variando o servidor de destino no payload
    NS_LOG_UNCOND("Client Application: Scheduled message to Server1 at 2 seconds");
    Simulator::Schedule(Seconds(2.0),
                        &ClientApp::SendRequest,
                        this,
                        "Server1: Ola sou o servidor 1");
    NS_LOG_UNCOND("Client Application: Scheduled message to Server2 at 5 seconds");
    Simulator::Schedule(Seconds(5.0),
                        &ClientApp::SendRequest,
                        this,
                        "Server2: Ola sou o servidor 2");
}

void
ClientApp::SendRequest(std::string message)
{
    Ptr<Packet> packet = Create<Packet>((uint8_t*)message.c_str(), message.length());
    this->internalSocket->Send(packet);
    NS_LOG_UNCOND("Client Application: Sent '" << message << "' to gateway at "
                                               << Simulator::Now().GetSeconds() << "s");
}

void
ClientApp::StopApplication(void)
{
    if (this->internalSocket)
    {
        NS_LOG_UNCOND("Client Application: Closing client socket on node " << GetNode()->GetId());
        this->internalSocket->Close();
    }
}
