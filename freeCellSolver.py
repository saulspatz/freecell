# Also try game
#178, #194, #454, #657, #829, #1025, #1403, #1651, #3015, #3199, #3289,
#4631, #6182, #6834, #7303, #7382, #7631, #7700, #8604, #8820, #9787,
#12006, #13015, #13304, #13970, #13996, #14107, #14991,
#15915, #15710, #15978, #16202
#16315, #16349, #16575 #16724,#17211, #18681
#19557, #20867, #21319, #23733, #24076, #25016,
#25269, #25315, #26061, #26576,
#26661, # #26693, #27327, #29128, #29596,
#30057, #31370, #31418, #31675, #31772

class Tableau(object):
    
    def __init__(self, deck):
        self.free = []                                                        # up to four free cards
        self.foundations = [0,0,0,0]                                   # top card in foundation piles
                                                                                  # in suit order (clubs to spades)
        self.piles = [[]]                                                   # the eight cascade piles; pile 0 is a dummy
        self.history = []                                                   # move history
        for i in range(4):
            cards = deck[7*i:7*(i+1)]
            self.piles.append([Card(c) for c in cards])
        for i in range(4):
            cards = deck[6*i:6*(i+1)]
            self.piles.append([Card(c) for c in cards])
        self.makeForcedMoves()
        self.moves = self.listMoves()

    def __str__(self):
        piles=sorted(self.piles)
        free = sorted(self.free)
        return str(piles)+str(free)
    
    def makeForcedMoves(self):
        # "Forced" moves are moves to the foundations that cannot possibly hurt.
        # A move is forced if the card played cannot possibly have any use.
        # An Ace is always forced.
        # A card is forced if the two cards that could be played on it have already
        # been played to the foundations, so a red foour is forced is both black
        # threes have been played to the foundations.  
        # Also, a move is forced if all cards two below its rank have been played to
        # the foundations.  If all deuces have been palyed to the foundations, a red 
        # four is forced.  The black threes have no value, since the red deuces have
        # been played up, and there is no need to keep the red four as a parking place for
        # a black three; the three can be played up, since the deuces have been.
        
        moved = False
        found = self.foundations
        for idx, p in enumerate(self.piles):
            if not p: continue
            card = p[-1]
            rank, suit = card.rank, card.suit
            if suit < 2:
                opp = found[2:]     # opposite color foundations
            else:
                opp = found[:2]
            if min(opp) >= rank-1 or min(found) >= rank-2:
                moved = True
                del p[-1]
                self.foundations[suit] += 1
                self.history.append( ('FORCED', idx, card, 'FOUND') )
                                                  
        for card in self.free:
            rank, suit = card.rank, card.suit
            if suit < 2:
                opp = found[2:]     # opposite color foundations
            else:
                opp = found[:2]
            if min(opp) >= rank-1 or min(found) >= rank-2:
                moved = True
                self.free.remove(card)
                self.foundations[suit] += 1
                self.history.append( ('FORCED', 'FREE', card, 'FOUND') )
        if moved:
            self.makeForcedMoves()    # a forced moved may force other moves
            
    def unMakeForcedMoves(self):
        while self.history[-1][0] == 'FORCED':
            val, source, card, dest = self.history.pop(-1)
            self.foundations[card.suit] -= 1
            if source == 'FREE':                
                self.free.append(card)
            else:
                self.piles[source].append(card)
                
    def solve(self):
        self.makeForcedMoves()
        moves = self.listMoves()
        for move in moves:
            self.makeMove(move)
            if self.solve():
                return True
            self.unMakeMove(move)
        self.unMakeForcedMoves()
        return False
                
    def makeMove(self, move):
        self.history.append(move)
        val, source, card, dest = move
        if  dest == 'FOUND':
            self.foundations[card.suit] += 1
            if source == 'FREE':
                self.free.remove(card)
            else:
                del self.piles[source][-1]
        elif dest == 'FREE':
            self.free.append(card)
            del self.piles[source][-1]

        # dest is a pile if we get here
        
        elif source == 'FREE':
            self.free.remove(card)
            self.piles[dest].append(card)
            
        # source is also a pile  if we get here
        
        elif self.piles[source][-1] == card:
            self.piles[dest].append(card)
            del self.piles[source][-1]
            
        else:   # more than one card moved
            idx = self.piles[source].index(card)
            self.piles[dest].extend(self.piles[source][idx:])
            self.piles[source][idx:] = []   
                                
    def listMoves(self):
        pass
    
    def unMakeMove(self, move):
        val, source, card, dest = self.history.pop(-1)
        if  dest == 'FOUND':
            self.foundations[card.suit] -= 1
            if source == 'FREE':
                self.free.append(card)
            else:
                self.piles[source].append(card)
        elif dest == 'FREE':
            self.free.remove(card)
            self.piles[source].append(card)
            
        # dest is a pile if we get here
        
        elif source == 'FREE':
            self.free.append(card)
            del self.piles[dest][-1]
            
        # source is also a pile  if we get here
        
        elif self.piles[dest][-1] == card:
            self.piles[source].append(card)
            del self.piles[dest][-1]
            
        else:   # more than one card moved
            idx = self.piles[dest].index(card)
            self.piles[source].extend(self.piles[dest][idx:])
            self.piles[dest][idx:] = []

    
    
class Card(object):
    ranks = '0A23456789TJQK'  # 0 is dummy to avoid special cases in the code
    suits = 'CSDH'
    black = 0
    red = 1
    colors = dict({0:black, 1:black, 2:red, 3:red, 'C':black, 'S':black, 'D':red, 'H':red}) 
    
    def __init__(self, card):
        self.str = card
        self.rank = self.ranks.index(card[0])
        self.suit = self.suits.index(card[1])
        self.color = self.colors[card[1]]

    def __str__(self):        
        return self.str

    def __repr__(self):
        return self.str

def main():
    global tab
    deck = []
    deck.extend(['QS','5C','6C','JC','3D','4S','AS'])
    deck.extend(['7S','7H','3C','4D','8D','KH','5S'])
    deck.extend(['9S','KC','3S','8C','6H','8S','6D'])
    deck.extend(['TC','AD','QH','5H','7D','TD','TS'])
    deck.extend(['2D','2H','KS','9C','AC','9D'])
    deck.extend(['7C','QC','8H','2S','9H','QD'])
    deck.extend(['4C','TH','4H','JS','AH','6S'])
    deck.extend(['KD','3H','5D','JH','JD','2C'])
##    test = [card.rank + 13*card.suit for card in test]
##    test.sort()
##    assert test == range(52)
    tab = Tableau(deck)
    tab.solve()

if __name__ == '__main__':
    main()
