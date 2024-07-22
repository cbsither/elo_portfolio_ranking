
class Evaluation:

    def __init__(self):
        pass

    def above_below_equal(self, s1: float, s2: float):
        if s1 > s2:
            return 1
        elif s1 == s2:
            return 0
        elif s1 < s2:
            return -1

    def overlap(self, min1, max1, min2, max2):
        start = max(min1, min2)
        end = min(max1, max2)
        d = end - start
        return d

    def pct_overlap(self, min1, max1, min2, max2):

        d = self.overlap(min1, max1, min2, max2)

        if d < 0:
            return 0
        else:
            return d / (max1 - min1)

    def above_below_equal_bid_ask(self, s1: float, s2: float, bid_ask_s1: float, bid_ask_s2: float, decision: float):

        s1_range = [s1 + bid_ask_s1, s1 - bid_ask_s1]
        s2_range = [s2 + bid_ask_s2, s2 - bid_ask_s2]

        d = self.pct_overlap(min1=s1_range[1], max1=s1_range[0],
                             min2=s2_range[1], max2=s2_range[0])

        if d > decision:
            return 0
        elif s1_range[0] > s2_range[0]:
            return 1
        elif s1_range[0] < s2_range[0]:
            return -1