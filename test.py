import numpy as np
from fairpyx import Instance, AllocationBuilder
from fairpyx.algorithms import hffd

# Define sample input
valuations = [
    [9, 7, 4, 3, 1],
    [6, 5, 3, 2, 1]
]
thresholds = [20, 18]

# Convert to numpy array for the Instance
valuations_np = np.array(valuations)

# Create Instance and AllocationBuilder
instance = Instance(valuations=valuations_np)
builder = AllocationBuilder(instance)

# Run the algorithm
result = hffd(builder, thresholds=thresholds)

# Print the result
print("=== HFFD Result ===")
print("Allocations:", result['allocations'])
print("Steps:", result['steps'])
print("Unallocated items:", result['unallocated'])

# Optionally: print total cost per agent
for agent, items in result['allocations'].items():
    total_cost = sum(valuations[agent][item] for item in items)
    print(f"Agent {agent}: Total cost = {total_cost}")
