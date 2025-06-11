"""
An implementation of the algorithm in:
"A Reduction from Chores Allocation to Job Scheduling", by Xin Huang and Erel Segal-Halevi (2024)
Local implementation for web demonstration
"""

from typing import Any, Mapping, Sequence, List, Dict
import logging
import numpy as np

logger = logging.getLogger(__name__)

class Instance:
    """A simplified version of the Instance class for our web demo"""
    def __init__(self, valuations: np.ndarray):
        self.valuations = valuations
        self.num_of_agents = len(valuations)
        self.num_of_items = len(valuations[0])

    def agent_item_value(self, agent: int, item: int) -> float:
        """Get the value of an item for an agent"""
        return float(self.valuations[agent][item])

class AllocationBuilder:
    """A simplified version of AllocationBuilder for our web demo"""
    def __init__(self, instance: Instance):
        self.instance = instance
        self._allocations: Dict[Any, List[Any]] = {}
        self._remaining_items = set(range(instance.num_of_items))
        self._remaining_agents = set(range(instance.num_of_agents))

    def remaining_agents(self):
        return self._remaining_agents

    def remaining_items(self):
        return self._remaining_items

    def give(self, agent: Any, item: Any) -> None:
        if agent not in self._allocations:
            self._allocations[agent] = []
        self._allocations[agent].append(item)
        self._remaining_items.remove(item)

    def get_allocations(self) -> Dict[Any, List[Any]]:
        return self._allocations

def hffd(
    builder: AllocationBuilder,
    *,
    thresholds: Mapping[Any, float] | Sequence[float],
    universal_order: Sequence[Any] | None = None,
) -> Dict[Any, List[Any]]:
    """
    Allocates chores to agents with heterogeneous costs under Identical-Order
    Preference (IDO), creating bundles A₁…Aₙ and giving each to an agent whose
    total cost stays ≤ τₐ.

    Parameters:
        - builder: AllocationBuilder – mutable helper that stores the instance and lets the algorithm assign items
        - thresholds: Mapping[Any, float] – per-agent cost limit τₐ that a bundle may not exceed
        - universal_order: Sequence[Any] | None – identical ranking of chores (largest → smallest)

    Returns:
        Dict[Any, List[Any]] – the allocation of items to agents
    """
    inst = builder.instance
    agents = list(builder.remaining_agents())
    items_0 = list(builder.remaining_items())

    # Normalize thresholds
    if not isinstance(thresholds, Mapping):
        if len(thresholds) != len(agents):
            raise ValueError("threshold list length must equal #agents")
        thresholds = dict(zip(agents, thresholds))
    if set(thresholds) != set(agents):
        raise ValueError("thresholds must specify every agent exactly once")

    tau = {a: float(thresholds[a]) for a in agents}

    # Decide common order
    order = list(universal_order) if universal_order is not None else items_0
    if set(order) != set(items_0):
        raise ValueError("universal_order must match remaining items exactly")

    # Pre-compute cost lookup
    cost = {(a, i): inst.agent_item_value(a, i) for a in agents for i in order}

    # Build bundles A₁, A₂, …
    remaining_items = set(order)
    agents_left = agents.copy()
    bundle_no = 0
    steps = []  # For visualization

    while agents_left and remaining_items:
        bundle: list[Any] = []

        # Pass 1 – collect chores into current bundle
        for i in order:
            if i not in remaining_items:
                continue
            if any(sum(cost[(a, j)] for j in bundle) + cost[(a, i)] <= tau[a]
                   for a in agents_left):
                bundle.append(i)

        if not bundle:  # safeguard (should not occur under IDO)
            break

        # Pass 2 – choose first agent who can accept full bundle
        chosen = next(a for a in agents_left
                     if sum(cost[(a, j)] for j in bundle) <= tau[a])

        bundle_cost = sum(cost[(chosen, j)] for j in bundle)
        bundle_no += 1
        
        # Record step for visualization
        steps.append({
            'step': bundle_no,
            'agent': chosen,
            'bundle': bundle.copy(),
            'cost': bundle_cost,
            'description': f'Bundle #{bundle_no} → Agent {chosen}: {bundle} (cost {bundle_cost:.0f})'
        })

        # Assign bundle
        for j in bundle:
            builder.give(chosen, j)
            remaining_items.remove(j)

        tau[chosen] -= bundle_cost
        agents_left.remove(chosen)

    return {
        'allocations': builder.get_allocations(),
        'steps': steps,
        'unallocated': sorted(remaining_items) if remaining_items else []
    } 