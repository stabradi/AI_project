import CC
import sys


# keeps track of the origin time of packets. Index with (origin addr, seq. no)
otime = {}

# this takes two links, and handles the main link between them, along with the main send queues
# think of it as the line between the two routers in the dumbell
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
            self.recving_link.send(p[0],p[1])
        for p in recv_packets:
            print('p: '+str(p))
            self.sending_link.send(p[0],p[1])
    def tock(self):
        global global_time
        self.sending_link.tick()
        self.recving_link.tick()
        global_time += 1                             # this is where the global time goes up

class Link:
    # TODO P2 call listeners when send, receive, enqueue, or drop events occur
    # takes a dict of link address pairs
    def __init__(self,queue_length,agent_side):
        self.agent_side = agent_side # this is a boolean flag that determines if the link is connected to the sending agents or not for purposes of addressing
        self.addr_link_pairs = {}
        self.addr_buffer_pairs = {}
#        for key in self.addr_link_pairs:
#            self.addr_buffer_pairs[key] = []
        self.queue_length = queue_length

        # Routines to call when certain events occur
        self.enQ_events = []
        self.send_events = []
        self.recv_events = []
        self.drop_events = []

    def register(self,addr,link):
        self.addr_link_pairs[addr] = link
        self.addr_buffer_pairs[addr] = []

    def tick(self):
        for key in self.addr_link_pairs:
            self.addr_link_pairs[key].tick()

    # Return the first x packets from the buffer for address y, then clear that
    # x packets. The caller knows how much data its link allows, so it requests
    # that much data per tick.
    def recv(self,number_of_packets,recving_addr):
        global global_time
        # get the first x packets
        ret = self.addr_buffer_pairs[recving_addr][:number_of_packets]
        # Trigger listeners
        for pkt in self.addr_buffer_pairs[recving_addr]:
            for routine in self.send_events:
                # If recving_addr is 0, it means the packet is a tuple of (final
                # destination, seq_no; we need to unpack it.
                routine(global_time,
                        0-recving_addr if recving_addr else 0-pkt[0],
                        recving_addr if recving_addr else pkt[0],
                        "lnk_0" if self.agent_side else "lnk_1",
                        pkt if recving_addr else pkt[1][0])
        #clear the sent packets from the buffer
        self.addr_buffer_pairs[recving_addr] = self.addr_buffer_pairs[recving_addr][number_of_packets:]
        print ret
        print recving_addr
        return ret

    def send(self,addr,packets):
        global global_time
        bpairs = self.addr_buffer_pairs # temporary variable
        # this is how you denote whether the link is on the side of the sender
        # or the reciever, it creates something like
        # (real_addr, [packet, packet, ...])
        # true agent_side means that positive addresses are on this side of the net
        print(str(bpairs) \
              + ' ' + str(self.agent_side) \
              + ' ' + str(addr))

        # If agent_side is true, we are on the sender's end and want to
        # transmit to negative addresses. If it is false, we are on the
        # receiver's end and want to transmit to positive addresses.
        if (self.agent_side == (addr < 0)) and addr != 0: 
            bpairs[0] += [(addr, [p]) for p in packets]
            # Notify listners of any dropped packets
            drops = bpairs[0][self.queue_length:]
            for pkt in drops:
                for routine in self.drop_events:
                    routine(global_time,
                            0-addr if addr else 0-pkt[0],
                            addr if addr else pkt[0],
                            "link_0" if self.agent_side else "link_1",
                            pkt if addr else pkt[1][0])
            # Drop the packets
            bpairs[0] = bpairs[0][:self.queue_length]
        # Some traffic is "through" traffic.
        else:
            bpairs[addr] += packets
            bpairs[addr] = bpairs[addr][:self.queue_length]

    # Call these to register listeners with the link
    def on_send(self, routine):
        self.send_events.append(routine)
    def on_recv(self, routine):
        self.recv_events.append(routine)
    def on_enQ(self, routine):
        self.recv_events.append(routine)
    def on_drop(self, routine):
        self.drop_events.append(routine)

class sending_agent:
    # TODO P2 call listeners when success events occur
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

        self.success_events = [] # Routine to call when we receive a valid ACK

    def tick(self):
        self.handle_input(self.link.recv(self.bandwidth,self.host_addr))
        packets = self.generate_packets()
        self.link.send(self.goal_addr,self.generate_packets())

    # We only ever receive ACKs; our CC figures out when to retransmit based
    # on the ACKs we receive.
    def handle_input(self,incoming_packets):
        global global_time
        # call listeners
        for p in incoming_packets:
            for routine in self.success_events:
                print otime
                routine(global_time,
                        self.host_addr,
                        1-self.host_addr,
                        "agent %d" % self.host_addr,
                        p,
                        otime[(self.host_addr,p)])
            self.cc.handle_ack(p)

    def generate_packets(self):
        global global_time
        rtn = self.cc.get_pending_sends()
        for pkt in rtn:
            print "new otime:"
            otime[(self.host_addr, pkt)] = global_time
            print otime
        return rtn

    def on_success(self, routine):
        self.success_events.append(routine)

class recving_agent:
    def __init__(self,link,addr):
        self.link = link
        self.addr_host = addr
        self.goal_addr = 0-addr # see sending_agent.goal_addr for an explanation
        self.last_in_order_seq = 0 # we have received no packets yet.
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

# The Oracle registers listeners with the various network objects and is thus 
# able to keep detailed logs to track what is going on in the network.
class Oracle:
    def __init__(self):
        self.events = []
        self.logfiles = []
        self.logloc = 0
    
    # Start listening for events on a link
    def reg_link(self, link):
        link.on_drop(self.drop)
        link.on_send(self.send)
        link.on_recv(self.recv)
        link.on_enQ(self.enQ)

    # Start listening for events on an agent
    def reg_agt(self, agt):
        agt.on_success(self.success)
    
    # Start logging events
    def begin_log(self,f):
        self.logfiles.append(f)

    def flush_logs(self):
        for event in self.events[self.logloc:]:
            for f in self.logfiles:
                f.write(event.log_str())
        self.logloc = len(self.events)

    def drop(self, time, src, dst, obj, seqno):
        self.events.append(DropEvent(time, src, dst, obj, seqno))
        print "Drop!"

    def enQ(self, time, src, dst, obj, seqno):
        self.events.append(EnQEvent(time, src, dst, obj, seqno))
    
    def success(self, time, src, dst, obj, seqno, sent):
        self.events.append(TransmitSuccessEvent(time,src,seqno,dst,sent))
        print "Success"

    def send(self, time, src, dst, obj, seqno):
        self.events.append(SendEvent(time, src, dst, obj, seqno))

    def recv(self, time, src, dst, obj, seqno):
        self.events.append(RecvEvent(time, src, dst, obj, seqno))

# Base class for simulation events. DO NOT INSTANTIATE.
class SimEvent:
    def __init__(self, symbol, time, src, dst, obj, seqno):
        self.time = time # simulation time the event was reported
        self.src = src # the address that originated the packet
        self.dst = dst # the destination address of the packet
        self.obj = obj # the simulation object reporting the event
        self.seqno = seqno # sequence number of packet
        self.symbol = symbol # symbol to represent this event type in a log file
    def log_str(self):
        print "--------------"
        print self.symbol
        print self.time
        print self.src
        print self.dst
        print self.seqno
        return "%s %4d %s %d %d %4d" % \
            (self.symbol, self.time, self.obj, self.src, self.dst, self.seqno)
    
class EnQEvent(SimEvent):
    def __init__(self, time, src, dst, obj, seqno):
        SimEvent.__init__(self, "Q", time, src, dst, obj, seqno)

class SendEvent(SimEvent):
    def __init__(self, time, src, dst, obj, seqno):
        SimEvent.__init__(self, "S", time, src, dst, obj, seqno)
        self.dst = dst

class RecvEvent(SimEvent):
    def __init__(self, time, src, dst, obj, seqno):
        SimEvent.__init__(self, "R", time, src, dst, obj, seqno)
        self.src = src

class DropEvent(SimEvent):
    def __init__(self, time,src, dst, obj, seqno):
        SimEvent.__init__(self, "D", time, src, dst, obj, seqno)

# Signifies the receipt of an acknowledgment by a sender
class TransmitSuccessEvent(SimEvent):
    def __init__(self, time, obj, src, dst, seqno, sent):
        SimEvent.__init__(self, "A", time, src, dst, obj, seqno)
        self.sent = sent # Simulation time the packet was sent
        self.rtt = time - sent # Round trip time for this packet

def main(argv=None):
    if argv==None:
        argv = sys.argv
    # this is the global time, it goes up every tick, it is global
    global global_time
    global_time = 0
    sending_link = Link(8,True)
    recving_link = Link(8,False)
    # TODO P4 accept neural network configuration and network topology from
    # command line or input file
    hidden_neurons = 7 
    max_send_queue = 5
    logfilename = "ssim.trc"
    oracle = Oracle()
    oracle.reg_link(sending_link)
    oracle.reg_link(recving_link)
    for i in range(1,5):
        snd_agt = sending_agent(sending_link,
                                CC.NCC(hidden_neurons,max_send_queue),
                                i)
        rcv_agt = recving_agent(recving_link,0-i)
        sending_link.register(i,snd_agt)
        recving_link.register(0-i,rcv_agt)
        oracle.reg_agt(snd_agt)
    try:
        logout = open(logfilename,'w')
        oracle.begin_log(logout)
    except IOError as e:
        print "Failed to open log."
    net = Master_link(sending_link,recving_link)
    net.tock()
    oracle.flush_logs()
    net.tock()
    oracle.flush_logs()
    net.tock()
    oracle.flush_logs()
    logout.close()


if __name__ == "__main__":
    main()
