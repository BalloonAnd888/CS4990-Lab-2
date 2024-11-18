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
        # Track hints for all cards in other players' hands
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

        # Play aggressively if game is near end
        if cards_left < 5 or hits >= 2:
            for i, k in enumerate(my_knowledge):
                if util.maybe_playable(k, board):
                    return Action(PLAY, card_index=i)  
                  
        # Give hints
        if hints > 0:
            # Play clue
            for player, hand in enumerate(hands):
                if player != nr:
                    for card_index, card in enumerate(hand):
                        if card.is_playable(board):
                            play_hint = util.filter_actions(HINT_COLOR, valid_actions) + util.filter_actions(HINT_RANK, valid_actions)
                            for hint in play_hint:
                                if hint.player == player and (hint.color == card.color or hint.rank == card.rank):
                                    return hint

            # Save clue       
            for player, hand in enumerate(hands):
                if player != nr:  # Consider only other players' hands
                    for card_index, card in enumerate(hand):
                        # Determine if the card is critical:
                        # - Rank 5 cards are always critical
                        # - A card is unique if all other copies are in trash or played
                        total_count = 3 if card.rank == 1 else (2 if card.rank in [2, 3, 4] else 1)
                        count_in_trash = sum(1 for c in trash if c == card)
                        count_in_played = sum(1 for c in played if c == card)
                        is_critical = (card.rank == 5) or ((count_in_trash + count_in_played) >= (total_count - 1))

                        if is_critical:
                            # Collect valid save hints
                            save_hint = util.filter_actions(HINT_COLOR, valid_actions) + util.filter_actions(HINT_RANK, valid_actions)
                            for hint in save_hint:
                                if hint.player == player and (hint.color == card.color or hint.rank == card.rank):
                                    return hint
                            
        return random.choice(util.filter_actions(DISCARD, valid_actions))

    def inform(self, action, player):
        if action.type in [PLAY, DISCARD]:
            if (player,action.card_index) in self.hints:
                self.hints[(player,action.card_index)] = set()
            for i in range(5):
                if (player,action.card_index+i+1) in self.hints:
                    self.hints[(player,action.card_index+i)] = self.hints[(player,action.card_index+i+1)]
                    self.hints[(player,action.card_index+i+1)] = set()

agent.register("guma", "Guma", Guma)




        


        # check if any card in your hand have a high chance its playable
        # give a hint 
        # discard a card that has a high chance its useless
            # don't want to discard a card that have a rank of 5
        # predicatable_discard = []
        # discard card if the card is in trash and played
        # if hits is closer to 3 and cards_left is closer to 0, play more aggressively
        # give hints that the card have a high chance of being playable (play clue)
        # If a hint can't be given due to the probability of the card being playable is low, discard
        # delayed play clue, receive a hint but also look at the other player
        # (save clue) must save all 5's, unique 2's and cards that have all other copies discarded
        # when a hint is for multiple cards, the leftmost is focused
        # Good Touch Principle
        # Save Principle
            # All 5's
            # Unique 2's (2's that are the only copy currently visible)
            # Critical cards (cards that have all other copies discarded)
            # Unique playable cards (playable cards that are the only copy currently visible)
        # Minimum Clue Value Principle
            # No Nonsense Clues
                # Only allowed to give play clues to actual playable cards
                # Only allowed to give save clues to the specific cards outline in Save Principle
                # If cannot give play or save clue, must discard
        # The Prompt is a promise that the player has the connecting card
        # The Finesse
        # Prompts > Finesses (prompts always take precedence over finesses)



    
