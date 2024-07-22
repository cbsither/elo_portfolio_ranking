import math

class Elo_Player:

    def __init__(self, rating = 1500, scalar=400):
        # For testing purposes, preload the values
        # assigned to an unrated player.
        self.__rating = rating
        self.__scalar = scalar

    def elo_rating(self, Rb):
        return 1 / (1 + 10 ** ((Rb - self.__rating) / self.__scalar))

    def Q_(self, R):
        return 10 ** (R / self.__scalar)

    def E_(self, Qa, Qb):
        return self.Q_(Qa) / (self.Q_(Qa) + self.Q_(Qb))

    def R_a(self, Sa, Ea, K):
        return self.__rating + (K * (Sa - Ea))

    def update(self, outcome, rating, K=32):
        self.__rating = self.R_a(K=K, Sa=outcome, Ea=self.elo_rating(Rb=rating))

    def online_update(self, outcomes, ratings, K=32):
        for i in range(0, len(outcomes)):
            self.update(K=K, outcome=outcomes[i], rating=ratings[i])

    def batch_update(self, outcomes, ratings, K=32):
        expected_score = [self.elo_rating(Rb=ratings[i]) for i in ratings]
        self.__rating = self.R_a(K=K, Sa=sum(outcomes), Ea=sum(expected_score))

    def win_probability(self, ratings):
        return [self.elo_rating(Rb=ratings[i]) for i in ratings]


class Glicko2_Player:
    # Code from: https://github.com/ryankirkman/pyglicko2/blob/master/glicko2.py
    # Class attribute
    # The system constant, which constrains
    # the change in volatility over time.
    _tau = 0.5

    def getRating(self):
        return (self.__rating * 173.7178) + 1500

    def setRating(self, rating):
        self.__rating = (rating - 1500) / 173.7178

    rating = property(getRating, setRating)

    def getRd(self):
        return self.__rd * 173.7178

    def setRd(self, rd):
        self.__rd = rd / 173.7178

    rd = property(getRd, setRd)

    def __init__(self, rating = 1500, rd = 350, vol = 0.06):
        # For testing purposes, preload the values
        # assigned to an unrated player.
        self.setRating(rating)
        self.setRd(rd)
        self.vol = vol

    def _preRatingRD(self):
        """ Calculates and updates the player's rating deviation for the
        beginning of a rating period.

        preRatingRD() -> None

        """
        self.__rd = math.sqrt(math.pow(self.__rd, 2) + math.pow(self.vol, 2))

    def update_player(self, rating_list, RD_list, outcome_list):
        """ Calculates the new rating and rating deviation of the player.

        update_player(list[int], list[int], list[bool]) -> None

        """
        # Convert the rating and rating deviation values for internal use.
        rating_list = [(x - 1500) / 173.7178 for x in rating_list]
        RD_list = [x / 173.7178 for x in RD_list]

        v = self._v(rating_list, RD_list)
        self.vol = self._newVol(rating_list, RD_list, outcome_list, v)
        self._preRatingRD()

        self.__rd = 1 / math.sqrt((1 / math.pow(self.__rd, 2)) + (1 / v))

        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self._g(RD_list[i]) * \
                       (outcome_list[i] - self._E(rating_list[i], RD_list[i]))
        self.__rating += math.pow(self.__rd, 2) * tempSum


    def _newVol(self, rating_list, RD_list, outcome_list, v):
        """ Calculating the new volatility as per the Glicko2 system.

        _newVol(list, list, list) -> float

        """
        i = 0
        delta = self._delta(rating_list, RD_list, outcome_list, v)
        a = math.log(math.pow(self.vol, 2))
        tau = self._tau
        x0 = a
        x1 = 0

        while x0 != x1:
            # New iteration, so x(i) becomes x(i-1)
            x0 = x1
            d = math.pow(self.__rating, 2) + v + math.exp(x0)
            h1 = -(x0 - a) / math.pow(tau, 2) - 0.5 * math.exp(x0) \
            / d + 0.5 * math.exp(x0) * math.pow(delta / d, 2)
            h2 = -1 / math.pow(tau, 2) - 0.5 * math.exp(x0) * \
            (math.pow(self.__rating, 2) + v) \
            / math.pow(d, 2) + 0.5 * math.pow(delta, 2) * math.exp(x0) \
            * (math.pow(self.__rating, 2) + v - math.exp(x0)) / math.pow(d, 3)
            x1 = x0 - (h1 / h2)

        return math.exp(x1 / 2)

    def _delta(self, rating_list, RD_list, outcome_list, v):
        """ The delta function of the Glicko2 system.

        _delta(list, list, list) -> float

        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self._g(RD_list[i]) * (outcome_list[i] - self._E(rating_list[i], RD_list[i]))
        return v * tempSum

    def _v(self, rating_list, RD_list):
        """ The v function of the Glicko2 system.

        _v(list[int], list[int]) -> float

        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempE = self._E(rating_list[i], RD_list[i])
            tempSum += math.pow(self._g(RD_list[i]), 2) * tempE * (1 - tempE)
        return 1 / tempSum

    def _E(self, p2rating, p2RD):
        """ The Glicko E function.

        _E(int) -> float

        """
        return 1 / (1 + math.exp(-1 * self._g(p2RD) * \
                                 (self.__rating - p2rating)))

    def _g(self, RD):
        """ The Glicko2 g(RD) function.

        _g() -> float

        """
        return 1 / math.sqrt(1 + 3 * math.pow(RD, 2) / math.pow(math.pi, 2))

    def did_not_compete(self):
        """ Applies Step 6 of the algorithm. Use this for
        players who did not compete in the rating period.

        did_not_compete() -> None

        """
        self._preRatingRD()


    # New code below
    def reduce_impact(self, RD):
        return 1. / math.sqrt(1 + (3 * RD ** 2) / (math.pi ** 2))

    def expect_score(self, rating, other_rating, impact):
        return 1. / (1 + math.exp(-impact * (rating - other_rating)))

    def quality_1vs1(self, p2rating, p2RD):

        if isinstance(p2rating, list):
            quality_score = []
            for i in range(0, len(p2rating)):
                expected_score1 = self.expect_score(self.rating, p2rating[i], self.reduce_impact(self.rd))
                expected_score2 = self.expect_score(p2rating[i], self.rating, self.reduce_impact(p2RD[i]))
                expected_score = (expected_score1 + expected_score2) / 2
                quality_score.append(2 * (0.5 - abs(0.5 - expected_score)))
            return quality_score

        else:
            expected_score1 = self.expect_score(self.rating, p2rating, self.reduce_impact(self.rd))
            expected_score2 = self.expect_score(p2rating, self.rating, self.reduce_impact(p2RD))
            expected_score = (expected_score1 + expected_score2) / 2
        return 2 * (0.5 - abs(0.5 - expected_score))