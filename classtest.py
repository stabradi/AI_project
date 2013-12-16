from CC import Classifier
def main(argv=None):
    classy = Classifier (1, 1, 1, 10, 7)
    packet_ack_log = []
    packet_ack_log.append([1, 5, (4, 5, 5)])
    packet_ack_log.append([1, 7, (4, 5, 3)])
    packet_ack_log.append([1, 0, (8, 2, 2)])
    packet_ack_log.append([1, 0, (9, 2, 3)])
    print packet_ack_log
    classy.computeAndTrain(packet_ack_log)
    NN = classy.getNet()
    print NN.activate(packet_ack_log[0][2])



if __name__ == "__main__":
    main()
    


