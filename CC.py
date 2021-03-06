from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.datasets import SupervisedDataSet
import sys
import getopt
import pipes


class Classifier:

    #I'm not sure where to get the number of packets dropped while the packet in
    #question was in queue
    def __init__(self, alpha, beta, gamma, hidden_neurons, max_send_queue):
        self.alpha = alpha #prize for being successfully acked
        self.beta = beta #penalty for having other packets drop around you
        self.gamma = gamma #penalty for being dropped
        self.net = buildNetwork(3, hidden_neurons, max_send_queue)
        self.data_set = SupervisedDataSet(3, max_send_queue)
    
    def computeUtility(self, packet_ack_log):
        #initialize utility
        utility = []
        for ii in range(len(packet_ack_log)):
            utility.append(0)
            #When the time sent is greater than the time recieved, that means
            #the packet was never recieved. Apply packet dropped penalty.
            if packet_ack_log[ii][0] > packet_ack_log[ii][1]:
                utility[ii] -= self.gamma
            #Else the packet must have made it! Give the NN a cookie.
            else:
                utility[ii] += self.alpha
        return utility

    def addToTrainingSet(self, state, lineOfFire):
        self.data_set.addSample(state, lineOfFire)

    def trainNet(self):
        trainer = BackpropTrainer(self.net, self.data_set)
        trainer.trainUntilConvergence()

    def computeAndTrain(self, packet_ack_log):
        utility = self.computeUtility(packet_ack_log)
        #whether we should have fired the packet or not. 1 means we should have
        #0 means we should not have
        lineOfFire = []
        for i in range(len(utility)):
            lineOfFire.append(0)
            #if we gained utility from the packet, we should have sent it.
            if utility[i] > 0:
                lineOfFire[i] = 1
            self.addToTrainingSet(packet_ack_log[i][2], lineOfFire[i])
        self.trainNet();

    def getNet(self):
        return self.net

# An individual congestion control algorithm, expressed as a neural network.
class NCC:
    def __init__(self, hidden_neurons, max_send_queue):
        self.net = buildNetwork(3, hidden_neurons, max_send_queue)
        self.packets_in_flight = []

        # We use these three parameters to decide when to send packets.
        # (note, EWMA stands for exponentially weighted moving average)
        self.ack_ewma = 1 # EWMA of interval acknowledgments
        self.send_ewma = 1 # EWMA of interval between sends (based on ACKs)
        self.rtt_ratio = 1 # Latest RTT divided by minimum observed RTT

        self.number_of_packets_to_send = 0
        self.next_unsent = 1
        self.packet_ack_log = {}
        self.last_ack_in_seq = 0
        self.ticks = 0

    def enqueue(self,packet):
        self.packets_in_flight.append(packet)
        self.packet_ack_log[packet] = [self.ticks,0,None]
        #(time created, time acked, input to NN)

    # this should return some packets to transmit probably (should it? Are we
    # planning to deprecate get_pending_sends? -DM)
    def handle_ack(self, response_number): 
        next_queue_batch = []
        for p in self.packets_in_flight:
            if p > response_number:
                next_queue_batch.append(p)
            else:                          # this means it was taken out of the queue, better log at what time it was taken out of the queue
                for i in range(self.last_ack_in_seq,response_number):
                    # Log time of packet ACK
                    # TODO P2 Modify EWMAs and RTT ratio
                    self.packet_ack_log[i+1][1] = self.ticks
                    
                if self.last_ack_in_seq < response_number:
                    self.last_ack_in_seq = response_number
                    self.packets_in_flight = next_queue_batch
        #foo[:n-1] + foo[n:] + [None]
                        
    def send_n_packets(self,n):
        self.number_of_packets_to_send += n

    def get_pending_sends(self):
        sends = self.net.activate([self.ack_ewma, self.send_ewma, self.rtt_ratio])
        SQ = []
        i = 0
        for s in sends:
            if s > 0: # I guess we can play around with this number if we want, I am not sure if that is a good idea
        #        self.enqueue(self.next_unsent + i)
                SQ.append(self.next_unsent + i)
            i += 1
        if SQ == []:
            return []
        SQ_x = SQ[-1]
        if (SQ_x - self.next_unsent) > self.number_of_packets_to_send:
            SQ_x = self.next_unsent + self.number_of_packets_to_send
        SQ = range(self.next_unsent, SQ_x)
        self.next_unsent = SQ_x
        print SQ
        for s in SQ:
            self.enqueue(s)
            self.number_of_packets_to_send -= 1
        return SQ # this should be an array of sequence numbers or something

    def tick(self):
        self.ticks += 1


def main(argv=None):
    if argv==None:
        argv = sys.argv
    input_file = argv[1] #first arg is the name of the input pipe
    output_file = argv[2] #second arg is the name of the output pipe
    CC_object = NCC(int(argv[3]),int(argv[4])) # hidden_neurons, max_send_queue
    OF = pipes.Template().open(output_file,'w')
    IF = open(input_file)
    total_packet_count = 0
    while True: # this is the main loop
        for x in IF.read().split():
            print(x)
            if x[0:3] == 'ack':                                           # handle an ACK from the network
                CC_object.handle_ack(int(x[3:]))
            elif x[0:3] == 'NQN':                                           # enqueue n new packets
                    CC_object.send_n_packets(int(x[3:]))
            elif x[0:3] == 'TCK':
                for p in CC_object.get_pending_sends():
                    OF.write('snd'+str(p)+'\n')
                OF.flush()
                CC_object.tick()
            elif x[0:3] == 'HLT':                                           # handle shutdown command
                return

if __name__ == "__main__":
    main()
