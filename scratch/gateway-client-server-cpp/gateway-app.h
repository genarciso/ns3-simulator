#ifndef GATEWAY_APP
#define GATEWAY_APP

#include "ns3/applications-module.h"
#include "ns3/log.h"
#include "ns3/network-module.h"

using namespace ns3;

class GatewayApp : public Application
{
  public:
    GatewayApp();
    virtual ~GatewayApp();
    void Setup(Ipv4Address server1Ip, Ipv4Address server2Ip, uint16_t port);

  private:
    Ptr<Socket> internalSocket;
    Ipv4Address server1Addr;
    Ipv4Address server2Addr;
    uint16_t port;

    virtual void StartApplication(void);
    void HandleRead(Ptr<Socket> socket);
    void ForwardPacket(Ptr<Packet> packet, Ipv4Address target);
    virtual void StopApplication(void);
};
#endif // GATEWAY_APP
