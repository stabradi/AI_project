import CC
import sys

# this takes two links, and handles the main link between them, along with the main send queues
# think of it as the line between the two routers in the dumbel
class Master_link:
    def __init__(self,sending_link,recving_link):
        sending_link.register(0,self)
        recving_link.register(0,self)
        self.sending_link = sending_link
        self.recving_link = recving_link
    def tick(self):
        send_packets = self.sending_link.recv(100,0) # get up to 100 packets, they are cross network packets, so they have an addr of 0
        recv_packets = self.recving_link.recv(100,0)
        for p in send_packets:
            print('p: '+str(p))
            self.sending_link.send(p[0],p[1])
        for p in recv_packets:
            print('p: '+str(p))
            self.recving_link.send(p[0],p[1])
    def tock(self):
        self.sending_link.tick()
        self.recving_link.tick()

class Link:
    # takes a dict of link address pairs
    def __init__(self,queue_length,agent_side):
        self.agent_side = agent_side # this is a boolean flag that determines if the link is connected to the sending agents or not for purposes of addressing
        self.addr_link_pairs = {}
        self.addr_buffer_pairs = {}
#        for key in self.addr_link_pairs:
#            self.addr_buffer_pairs[key] = []
        self.queue_length = queue_length

    def register(self,addr,link):
        self.addr_link_pairs[addr] = link
        self.addr_buffer_pairs[addr] = []

    def tick(self):
        for key in self.addr_link_pairs:
            self.addr_link_pairs[key].tick()

    # Return the first x bytes from the buffer for address y, then clear that
    # many bytes. The caller knows how much data its link allows, so it requests
    # that much data per tick.
    def recv(self,number_of_packets,recving_addr): 
        ret = self.addr_buffer_pairs[recving_addr][:number_of_packets]
        self.addr_buffer_pairs[recving_addr] = self.addr_buffer_pairs[recving_addr][number_of_packets:]
        return ret

    def send(self,addr,packets):
        bpairs = self.addr_buffer_pairs # temporary variable
        # this is how you denote whether the link is on the side of the sender
        # or the reciever, it creates something like
        # (real_addr, [packet, packet, ...])
        # true agent_side means that positive addresses are on this side of the net
        print(str(bpairs) \
              + ' ' + str(self.agent_side) \
              + ' ' + str(addr))

        if self.agent_side and (addr < 0): 
            bpairs[0] += [(addr, [p]) for p in packets]
            bpairs[0] = bpairs[0][:self.queue_length]
            return
        elif (not self.agent_side) and (addr > 0): 
                    bpairs[0] += [(addr, [p]) for p in packets]
                    bpairs[0] = bpairs[0][:self.queue_length]
                    return
        bpairs[addr] += packets
        bpairs[addr] = bpairs[addr][:self.queue_length]

class sending_agent:
    def __init__(self,link,cc,addr):
        self.link = link
        self.cc = cc # The congestion control algorithm to use
        self.host_addr = addr
        # This is a bit of a hack; we treat adresses as signed integers, and
        # each agent communicates with the agent whose address is opposite; the
        # upshot is that no agent can have more than one connection open, which
        # works fine for our purposes.
        self.goal_addr = 0-addr

        self.bandwidth = 3 # default bandwidth
        self.mission = 45 # default number of packets to be sent 

    def tick(self):
        self.handle_input(self.link.recv(self.bandwidth,self.host_addr))
        self.link.send(self.goal_addr,self.generate_packets())

    # We only ever receive ACKs; our CC figures out when to retransmit based
    # on the ACKs we receive.
    def handle_input(self,incoming_packets):
        for p in incoming_packets:
            self.cc.handle_ack(p)

    def generate_packets(self):
        return self.cc.get_pending_sends()

class recving_agent:
    def __init__(self,link,addr):
        self.link = link
        self.addr_host = addr
        self.goal_addr = 0-addr # see sending_agent.goal_addr for an explanation
        self.last_in_order_seq = -1 # -1 means we have received no packets yet.
        self.out_of_order_seqs = []
        self.sndQ = []
        self.bandwidth = 3 # default bandwidth

    def tick(self):
        self.handle_input(self.link.recv(self.bandwidth,self.addr_host))
        self.link.send(self.goal_addr,self.generate_packets())

    def handle_input(self,input_list):
        # TODO P3 write a helper function to encapsulate some of this logic
        while input_list != [] or self.out_of_order_seqs != []:
            if self.last_in_order_seq+1 in input_list:
                self.last_in_order_seq += 1
                input_list.remove(self.last_in_order_seq)
            elif self.last_in_order_seq+1 in self.out_of_order_seqs:
                self.last_in_order_seq += 1
                self.out_of_order_seqs.remove(self.last_in_order_seq)
            else:
                self.out_of_order_seqs += input_list
                return

    def generate_packets(self):
        # ACK the last in-order packet
        return [self.last_in_order_seq]

def main(argv=None):
    if argv==None:
        argv = sys.argv
    sending_link = Link(8,True)
    recving_link = Link(8,False)
    # TODO P4 accept neural network configuration and network topology from
    # command line or input file
    hidden_neurons = 7 
    max_send_queue = 5
    for i in range(1,5):
        sending_link.register(i,sending_agent(sending_link,CC.NCC(hidden_neurons,max_send_queue),i))
        recving_link.register(0-i,recving_agent(recving_link,0-i))
    net = Master_link(sending_link,recving_link)
    net.tock()
    net.tock()
    net.tock()


if __name__ == "__main__":
    main()
