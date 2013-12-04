from pybrain.tools.shortcuts import buildNetwork

class Packet:
    def __init__(self,data,response_number):
        self.data = data
        self.response_number = response_number
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
        response_position = 
        for i in range(len(self.send_queue)):
            
        self.send_queue = 
