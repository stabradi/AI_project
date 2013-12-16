#include "NNAgent.h"

NNAgent::NNAgent() : Agent(PT_UDP){
	// TODO
}

int NNAgent::Command(int argc, const char* const* argv){
	// TODO
	return(Agent::command(argc, argv));
}

static class MyAgentClass : public TclClass{
	public:
		MyagentClass() : TclClass("Agent/NN") {}
		TclObject* create(int argc, const char* const argv){
			return(new NNAgent());
		}
}
