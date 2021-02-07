import numpy as np
import torch


class KM_alg():
    """
    Krasnoselskii Mann (KM) Algorithm

    Purpose: Using input operators S(u) and T(u,d), solve the problem
             Find u  s.t.  u = (1 - alpha) * T(u; d) + alpha * S(u).
    We assume T is a neural network operator (from PyTorch).

    Example Code Snippet:
        KM  = KM_alg(S, T, alpha, device)
        u, depth  = KM(u0, d, eps)
        optimizer.zero_grad()
        y = KM.apply_T(u, d)
        output = loss(y, label)
        output.backward()
        optimizer.step()
    """
    def __init__(self, S, T, alpha: float, device,
                 max_depth=500, eps=1.0e-5):
        self.alpha = alpha
        self._S = S
        self._T = T
        self.max_depth = max_depth
        self.eps_tol = eps
        self._device = device

    def __repr__(self):
        output = 'KM_alg(\n'
        output += '      alpha       = %r\n'
        output += '      max depth   = %r\n'
        output += '      default eps = %r\n'
        output += '      device      = %r\n'
        output += ')'
        return output % (self.alpha, self.max_depth,
                         self.eps_tol, self._device)

    def __call__(self, u: torch.tensor,
                 d: torch.tensor, eps=-1) -> torch.tensor:
        """ Apply the KM algorithm.

            Training: Use this for forward prop, but do NOT use
                      is for back prop.

            Note: Because u contains batches of samples, we loop
                  until every sample converges, unless we hit the
                  max depth/number of iterations.
        """

        eps = eps if eps > 0 else self.eps_tol
        depth = 0.0
        u_prev = u.clone()
        indices = np.array(range(len(u[:, 0])))
        u = u.to(self._device)
        # Mask identifies not converged 'nc' samples (False = converged)
        nc = np.ones((1, u[:, 0].size()[0]), dtype=bool)
        nc = nc.reshape((nc.shape[1]))
        with torch.no_grad():
            while nc.any() > 0 and depth < self.max_depth:
                u_prev = u.clone()
                u = self.alpha * self._S(u) + (1 - self.alpha) * self._T(u, d)
                nc[nc > 0] = [torch.norm(u[i, :] - u_prev[i, :]) > eps
                              for i in indices[nc > 0]]
                depth += 1.0
        if depth >= self.max_depth:
            print("KM: Max Depth Reached - Break Forward Loop")
        return u.to(self._device), depth

    def apply_T(self, u: torch.tensor, d: torch.tensor) -> torch.tensor:
        """ Detach any gradients and then create gradient graph for
            a single application of T. This is used for backprop rather
            than calling the KM algorithm.
        """
        return self._T(u.detach(), d)

    def assign_ops(self, S, T):
        """ Use this to update T after every step of optimizer during training
        """
        self._S = S
        self._T = T
