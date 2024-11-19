from hanabi import *
import util
import agent
import random

def format_hint(h):
    if h == HINT_COLOR:
        return "color"
    return "rank"

class Guma(agent.Agent):
    def __init__(self, name, pnr):
        self.name = name
        self.hints = {}
        self.pnr = pnr
        self.explanation = []
    
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints, hits, cards_left):
        for player,hand in enumerate(hands):
            for card_index,_ in enumerate(hand):
                if (player,card_index) not in self.hints:
                    self.hints[(player,card_index)] = set()
        known = [""]*5
        for h in self.hints:
            pnr, card_index = h 
            if pnr != nr:
                known[card_index] = str(list(map(format_hint, self.hints[h])))
        self.explanation = [["hints received:"] + known]

        my_knowledge = knowledge[nr]
        
        potential_discards = []
        for i,k in enumerate(my_knowledge):
            if util.is_playable(k, board):
                return Action(PLAY, card_index=i)
            if util.is_useless(k, board):    
                potential_discards.append(i)
                
        if potential_discards:
            return Action(DISCARD, card_index=random.choice(potential_discards))
        
        playables = []        
        for player,hand in enumerate(hands):
            if player != nr:
                for card_index,card in enumerate(hand):
                    if card.is_playable(board):                              
                        playables.append((player,card_index))
        
        playables.sort(key=lambda which: -hands[which[0]][which[1]].rank)
        while playables and hints > 0:
            player,card_index = playables[0]
            knows_rank = True
            real_color = hands[player][card_index].color
            real_rank = hands[player][card_index].rank
            k = knowledge[player][card_index]
            
            hinttype = [HINT_COLOR, HINT_RANK]
            
            
            for h in self.hints[(player,card_index)]:
                hinttype.remove(h)
            
            t = None
            if hinttype:
                t = random.choice(hinttype)
            
            if t == HINT_RANK:
                for i,card in enumerate(hands[player]):
                    if card.rank == hands[player][card_index].rank:
                        self.hints[(player,i)].add(HINT_RANK)
                return Action(HINT_RANK, player=player, rank=hands[player][card_index].rank)
            if t == HINT_COLOR:
                for i,card in enumerate(hands[player]):
                    if card.color == hands[player][card_index].color:
                        self.hints[(player,i)].add(HINT_COLOR)
                return Action(HINT_COLOR, player=player, color=hands[player][card_index].color)
            
            playables = playables[1:]
        
        # if there is anything that could be discardable, discard it
        if potential_discards:
            return Action(DISCARD, card_index=random.choice(potential_discards))

        # if there are no other moves available, discard the middle card
        return Action(DISCARD, card_index = 2)
        
    def inform(self, action, player):
        if action.type in [PLAY, DISCARD]:
            if (player,action.card_index) in self.hints:
                self.hints[(player,action.card_index)] = set()
            for i in range(5):
                if (player,action.card_index+i+1) in self.hints:
                    self.hints[(player,action.card_index+i)] = self.hints[(player,action.card_index+i+1)]
                    self.hints[(player,action.card_index+i+1)] = set()

agent.register("guma", "Guma", Guma)
