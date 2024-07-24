import numpy as np


class BrownianMotion:

    def __init__(self):
        pass


    def brownian_motion(self, T, dt, mu, sigma):
        N = round(T/dt)
        t = np.linspace(0, T, N)
        W = np.random.normal(loc=mu, scale=sigma, size = N)
        W = np.cumsum(W)*np.sqrt(dt) ### standard brownian motion ###
        return W

    def geometric_brownian_motion(self, T, mu, sigma, S0, dt):
        """
        Start = 20
        t, S = GeometricBrownianMotion(T=1000, mu=0.000, sigma=0.04, S0=Start, dt=1)
        """
        N = round(T / dt)
        t = np.linspace(0, T, N)
        W = np.random.standard_normal(size=N)
        W = np.cumsum(W) * np.sqrt(dt)  ### standard brownian motion ###
        X = (mu - 0.5 * sigma ** 2) * t + sigma * W
        S = S0 * np.exp(X)  ### geometric brownian motion ###
        return t, S

    def generator(self, n_, T, dt, r_walk=[0, 0.05, 20], hyper_mu=None, hyper_sigma=None):

        all_paths = np.zeros((n_, T))

        if hyper_mu == None and hyper_sigma == None:

            for i in range(0, n_):
                t, S = self.geometric_brownian_motion(T=T,
                                                      mu=r_walk[0],
                                                      sigma=r_walk[1],
                                                      S0=r_walk[2], dt=dt)
                all_paths[i, :] = S

            return t, all_paths

        elif hyper_mu != None and hyper_sigma == None:

            all_mus = np.zeros((n_, T))
            all_paths = np.zeros((n_, T))

            for i in range(0, n_):
                mu_ = self.brownian_motion(T=T, dt=dt, mu=hyper_mu[0], sigma=hyper_mu[1])
                all_mus[i, :] = mu_

            for i in range(0, n_):
                t, S = self.geometric_brownian_motion(T=T,
                                                 mu=all_mus[i],
                                                 sigma=r_walk[1],
                                                 S0=r_walk[2], dt=dt)
                all_paths[i, :] = S

            return t, all_paths

        elif hyper_mu == None and hyper_sigma != None:

            all_sigmas = np.zeros((n_, T))
            all_paths = np.zeros((n_, T))

            for i in range(0, n_):
                t, sigma_ = self.geometric_brownian_motion(T=T, mu=hyper_sigma[0], sigma=hyper_sigma[1], S0=hyper_sigma[2], dt=dt)
                all_sigmas[i, :] = sigma_

            for i in range(0, n_):
                t, S = self.geometric_brownian_motion(T=T,
                                                 mu=r_walk[0],
                                                 sigma=all_sigmas[i],
                                                 S0=r_walk[2], dt=dt)
                all_paths[i, :] = S

            return t, all_paths

        else:

            all_sigmas = np.zeros((n_, T))
            all_mus = np.zeros((n_, T))
            all_paths = np.zeros((n_, T))

            for i in range(0, n_):
                mu_ = self.brownian_motion(T=T, dt=dt, mu=hyper_mu[0], sigma=hyper_mu[1])
                all_mus[i, :] = mu_

            for i in range(0, n_):
                t, sigma_ = self.geometric_brownian_motion(T=T, mu=hyper_sigma[0], sigma=hyper_sigma[1], S0=hyper_sigma[2], dt=dt)
                all_sigmas[i, :] = sigma_

            for i in range(0, n_):
                t, S = self.geometric_brownian_motion(T=T,
                                                 mu=all_mus[i],
                                                 sigma=all_sigmas[i],
                                                 S0=r_walk[2], dt=dt)
                all_paths[i, :] = S

            return t, all_paths