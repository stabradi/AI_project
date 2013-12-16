import CC
import sys

# this takes two links, and handles the main link between them, along with the main send queues
class Master_link:
    def __init__(self,sending_link,recving_link):
        self.sending_link = sending_link
        self.recving_link = recving_link
        self.global_send_queue = []
        self.
    def tick(self):
        for k in self.sending_link.addr_buffer_pairs:
            self.recving_link.send(k,self.sending_link.recv(10000,k))

class Link:
    # takes a dict of link address pairs
    def __init__(self,addr_link_pairs,queue_length):
        self.addr_link_pairs = addr_link_pairs
        self.addr_buffer_pairs = {}
        for key in addr_link_pairs:
            self.addr_buffer_pairs[key] = []
        self.queue_length = queue_length
    def tick(self):
        for key in self.addr_link_pairs:
            self.addr_link_pairs[key].tick()
    # the thing calling recv knows how much data its link allows, so it requests that much data per tick
    def recv(self,number_of_packets,recving_addr): 
        ret = self.addr_buffer_pairs[recving_addr][:number_of_packets]
        self.addr_buffer_pairs[recving_addr] = self.addr_buffer_pairs[recving_addr][number_of_packets:]
        return ret
    def send(self,addr,packets):
        self.addr_buffer_pairs[addr] += packets
        self.addr_buffer_pairs[addr] = self.addr_buffer_pairs[addr][:self.queue_length]

class sending_agent:
    def __init__(self,link,cc,addr):
        self.link = link
        self.cc = cc
        self.host_addr = addr
        self.goal_addr = 0-addr # this is because sending agents are never addressing other sending agents
        self.bandwidth = 3 # default bandwidth
        self.mission = 45 # default number of packets to be sent 
    def tick(self):
        self.handle_input(self.link.recv(self.addr))
        self.link.send(self.generate_packets())
    def handle_input(self,incoming_packets):
        for p in incoming_packets:
            self.cc.handle_ack(p)
    def generate_packets(self):
        return self.cc.get_pending_sends()

class recving_agent:
    def __init__(self,link,addr):
        self.link = link
        self.addr_host = addr
        self.goal_addr = 0-addr
        self.last_in_order_seq = -1
        self.out_of_order_seqs = []
        self.sndQ = []
    def tick(self):
        self.handle_input(self.link.recv())
        self.link.send(self.generate_packets())
    def handle_input(self,input_list):
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
        return [self.last_in_order_seq]

def main(argv=None):
    if argv==None:
        argv = sys.argv
    

if __name__ == "__main__":
    main()
