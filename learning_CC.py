from pybrain.tools.shortcuts import buildNetwork
import sys
import getopt
import pipes

class Packet:
    def __init__(self,data,response_number):
        self.data = data
        self.response_number = response_number
    # send_state is the state of the CC neural net at the time of sending
    # given that there are three numbers that are taken as input by the neural net, this is going to 
    def sent(self,ack_ewma,sent_ewma,rtt_ratio):
        self.ack_ewma = ack_ewma
        self.send_ewma = send_ewma
        self.rtt_ratio = rtt_ratio
    #state, action, event-sequence
    def terminate_packet(self):
        print('this hasnt been done')
        
class TcpwState:
    def __init__(self, ack_ewma, send_ewma, rtt_ratio):
        self.ack_ewma
        self.send_ewma
        self.rtt_ratio


class ordered_recieve_buffer:
    def __init__(self):
        self.next_packet_number = 0
        self.packets_unordered = {}
#takes the most recent packet and returns as much of the data queue as can now be assembled, this is done thusly to ensure that the data is still in order
    def recieved(self,packet):
        if packet.response_number == self.next_packet_number:
            packet_buffer = [packet]
            self.next_packet_number += 1
            while self.next_packet_number in self.packets_unordered:
                packet_buffer.append(self.packets_unordered.pop(self.next_packet_number))
                self.next_packet_number += 1
            return packet_buffer
        self.packets_unordered[packet.response_number] = packet
        return []

#Neural Congestion Controll
class NCC:
    def __init__(self, hidden_neurons, max_send_queue):
        self.net = buildNetwork(3, hidden_neurons, max_send_queue)
        self.send_queue = [None]*max_send_queue
        self.ack_ewma = 1
        self.send_ewma = 1
        self.rtt_ratio = 1
        self.packet_count = 0
    def enqueue(self,packet):
        self.send_queue.append(packet)
    def recieve(self,packet):
        if packet['type'] == 'ack':
            self.handle_ack(packet.response_number)
        else:
            self.add_response()
    def handle_ack(self, response_number):
        #foo[:n-1] + foo[n:] + [None]
        response_position = 5 # I have no idea what is happening
        for i in range(len(self.send_queue)):
            print('something went here, but clearly it was not committed')
        self.send_queue = 5 # I have no idea what is happening


def main(argv=None):
    if argv=None:
        argv = sys.argv
    input_file = argv[1] #first arg is the name of the input pipe
    output_file = argv[2] #second arg is the name of the output pipe
    OF = pipes.Template().open(output_file,'w')
    IF = open(input_file)


if __name__ == "__main__":
    main()
