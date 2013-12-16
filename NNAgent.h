include <stdio.h>
include <string.h>
include "agent.h"

class NNAgent : public TCPAgent{
	public:
		NNAgent()
		virtual void recv(Packet*, Handler*);
		virtual void sendmsg(int nbytes, const char * flags = 0);
		virtual void send_much(int force, int reason, int maxburst = 0);

	protected:
		int command(int argc, const char* const* argv);
	
	private:
		
}
