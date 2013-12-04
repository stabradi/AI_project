'''Trainer: Reinforcement learning system for TCP Worcester'''
from learning_cc import TcpwState

VALID_FATES = frozenset(["RECEIVED","DROPPED","CORRUPTED","REFUSED"])

class TcpwEvent:
    def __init__(self, ntreps, eterep):
        self.ntreps = ntreps
        self.eterep = eterep

class NTReport:
    def __init__(self, otherdrops, wait_time):
        self.otherdrops = otherdrops
        self.wait_time = wait_time

class ETEReport:
    def __init__(self, ttime, hops, fate):
        assert fate in VALID_FATES
        self.ttime = ttime
        self.hops = hops
        self.fate = fate

class Trainer:
    def __init__(self, alpha, beta, gamma):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
    def classify(state, action, event):
        '''state: State vector used to take an action; should be of
        TcpwState class.
        action: Action taken; should be TcpwAction class, or None.
        event: The event that occurred; should be TcpwEvent class, or None.
        returns a real-valued utility (a float) - higher is better.'''
        assert (action == None) == (event == None)
        if action == None:
            return 0.
        util = 0.
        if event.eterep.fate == "RECEIVED":
            util = self.alpha
        else:
            util = self.gamma
        for ntr in event.ntreps:
            util += (beta * ntr.otherdrops)
        return util
