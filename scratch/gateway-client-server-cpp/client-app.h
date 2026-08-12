#ifndef CLIENT_APP
#define CLIENT_APP

#include "ns3/applications-module.h"
#include "ns3/network-module.h"

using namespace ns3;

class ClientApp : public Application
{
  public:
    ClientApp();
    virtual ~ClientApp();
    void Setup(Ipv4Address gatewayAddr, uint16_t port);

  private:
    virtual void StartApplication(void) override;
    virtual void StopApplication(void) override;
    void SendRequest(std::string message);
    Ptr<Socket> internalSocket;
    Ipv4Address gatewayAddr;
    uint16_t port;
};
#endif // CLIENT_APP
