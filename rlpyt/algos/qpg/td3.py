
import torch

from rlpyt.algos.dpg.ddpg import DDPG
from rlpyt.utils.quick_args import save__init__args


class TD3(DDPG):

    def __init__(
            self,
            batch_size=100,
            training_intensity=100,  # data_consumption / data_generation
            target_update_tau=0.005,
            target_update_interval=2,
            policy_update_interval=2,
            mu_learning_rate=1e-3,
            q_learning_rate=1e-3,
            target_noise=0.2,
            target_noise_clip=0.5,
            **kwargs
            ):
        save__init__args(locals())
        super().__init__(**kwargs)

    def initialize(self, agent, n_itr, batch_spec, mid_batch_reset, examples):
        super().initialize(agent, n_itr, batch_spec, mid_batch_reset, examples)
        agent.set_target_noise(self.target_noise, self.target_noise_clip)

    def q_loss(self, samples):
        q1, q2 = self.agent.q(*samples.agent_inputs, samples.action)
        with torch.no_grad():
            target_q1, target_q2 = self.agent.target_q_at_mu(
                *samples.next_agent_inputs)  # Includes target action noise.
            target_q = torch.min(target_q1, target_q2)
        y = samples.reward + (1 - samples.done) * self.discount * target_q
        q1_losses = 0.5 * (y - q1) ** 2
        q2_losses = 0.5 * (y - q2) ** 2
        return q1_losses.mean() + q2_losses.mean()