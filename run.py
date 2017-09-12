from simulate import System

INITIAL_COST = -1
def cost_function(i, identities):
    if len(identities) == 1:
        return 0

    old_reputation = identities[i].reputation
    total_reputation = sum([identity.reputation for identity in identities[i + 1:]])
    if total_reputation <= 0:
        return old_reputation

    return old_reputation * abs(total_reputation / (total_reputation - old_reputation))

system = System(cost_function)

# make a good user
user = system.create_user(1, 0, 1, 1)
user.upload('first video')

# make a bad user with 5 identities
user = system.create_user(1, 0.5, 1, 5)
for _ in range(5):
    user.upload('test video')

for _ in range(5):
    system.interact(1)

print(system.reputation_history)
