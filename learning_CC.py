from pybrain.tools.shortcuts import buildNetwork

class ordered_recieve_buffer:
    def __init__(self):
        self.next_packet_number = 0
        self.packets_unordered = {}
    def recived(self,packet):
        if packet.response_number == self.next_packet_number:
            packet_buffer = [packet]
            self.next_packet_number += 1
            while self.next_packet_number in self.packets_unordered:
                self.next_packet_number += 1
                
#Neural Congestion Controll
class NCC:
    def __init__(self, hidden_neurons, max_send_queue):
        self.net = buildNetwork(3, hidden_neurons, max_send_queue)
        self.ack_ewma = 1
        self.send_ewma = 1
        self.rtt_ratio = 1
        self.packet_count = 0
        self.send_queue = []
    def enqueue(self,packet):
        self.send_queue.append(packet)
    def recieve(self,packet):
        if packet['type'] == 'ack':
            self.handle_ack(packet.response_number)
        else:
            self.add_response()
