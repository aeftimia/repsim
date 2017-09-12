'''
Simulate reputation of users
'''

import random

class User:
    def __init__(self,
                system,
                id,
                activity,
                malice,
                conformity,
                identities):

        '''
        Generate a user
        users can have more than one identity
        users will always like the content of its own identity
        users may elect not to game the system and use fake identities to vote for each other
        INPUTS
        - system: system to which user belongs
        - id: integer id number assigned to user
        - activity: odds of doing something at any given timestep
        - malice: Odds of interacting with between fake identies
        - conformity: Odds of voting with the majority for videos not owned by a fake identity
        - identities: number of fake identities to generate
        '''

        self.system = system
        self.id = id
        self.identities = [Identity(activity=activity,
                                    malice=malice,
                                    user=self,
                                    conformity=conformity,
                                    id=i) for i in range(identities)]
        self.__identity_id = 0

    def interact(self):
        for identity in self.identities:
            identity.interact()

    def upload(self, video):
        self.identities[self.__identity_id].upload(video)
        self.__identity_id += 1
        self.__identity_id %= len(self.identities)

    def __hash__(self):
        return  self.id


class Identity:
    def __init__(self,
                 activity,
                 malice,
                 user,
                 conformity,
                 id):
        '''
        Generate an identity
        '''
        self.activity = activity
        self.malice = malice
        self.user = user
        self.conformity = conformity
        self.system = user.system
        self.id = id
        self.uploads = {}
        self.reputation = self.system.initial_reputation 

    def interact(self):

        if random.random() > self.activity:
            return

        if random.random() < self.malice:
            # upvote one of my own identities
            identity = random.choice(self.user.identities)
            vote = ["thumbs_up"]
            video = random.choice(identity.uploads.keys())
        else:
            # vote on someone else's video
            identities = []
            for user in self.system.users:
                if user == self.user:
                    continue
                for identity in user.identities:
                    if identity.uploads:
                        identities.append(identity)
            
            if not identities:
                return

            random.choice(identities)

            video = random.choice(identity.uploads.keys())
            rating = identity.get_rating(video)
            majority_vote = rating > 0
            if random.random() < self.conformity and majority_vote:
                vote = ["thumbs_up"]
            else:
                vote = ["thumbs_down"]

        self.vote(identity, video, vote)

    def get_rating(self, video):
        rating = 0
        if "thumbs_up" in video:
            rating += len(video["thumbs_up"])
        
        if "thumbs_down" in video:
            rating -= len(video["thumbs_down"])

        return rating

    def vote(self, identity, video, votes):
        if self == identity:
            return

        for tag in votes:
            if tag not in identity.uploads[video]:
                identity.uploads[video][tag] = [identity]
            else:
                identity.uploads[video][tag].append(identity)

            identities = identity.uploads[video][tag]
            self.system.update_reputation(identities)

    def upload(self, video):
        '''
        Videos store a dict that maps
        tags to the list of users that voted for those tags
        in the order that they voted for them
        '''

        self.uploads[video] = {}

    def __hash__(self):
        return hash((self.user.id, self.id))

class System:

    def __init__(self, cost_function, initial_reputation=0):
        self.users = []
        self.cost_function = cost_function
        self.initial_reputation = initial_reputation

    def create_user(self,
                    activity=1.0,
                    malice=0.5,
                    conformity=0.5,
                    identities=1):

        user = User(self,
                len(self.users),
                activity,
                malice,
                conformity,
                identities)

        self.users.append(user)
        return user

    def interact(self, N=1):
        for _ in range(N):
            user_ids = range(len(self.users))
            random.shuffle(user_ids)
            for user_id in user_ids:
                self.users[user_id].interact()

    def update_reputation(self, identities):
        '''
        Update reputation of voters based on most recent vote
        in a list of identities that voted on a specific tag
        '''
        most_recent = identities[-1]
        num_identities = len(identities)
        total_reputation = sum([identity.reputation for identity in identities])
        
        cost_function = self.cost_function
        reputations = []
        for i, identity in enumerate(identities):
            reputations.append(cost_function(i, identities))

        for identity, reputation in zip(identities, reputations):
            identity.reputation = reputation

