# model.py Model for free cell solitaire

import random, itertools

ACE = 1
JACK = 11
QUEEN = 12
KING = 13
ALLRANKS = range(1, 14)      # one more than the highest value

# RANKNAMES is a list that maps a rank to a string.  It contains a
# dummy element at index 0 so it can be indexed directly with the card
# value.

SUITNAMES = ('spade', 'heart', 'diamond', 'club')
RANKNAMES = ["", "Ace"] + list(map(str, range(2, 11))) + ["Jack", "Queen", "King"]

DEAL = (0, 0, 10, 0)     # used in undo/redo stacks

class Stack(list):
    '''
    A pile of cards.
    The base class deals with the essential facilities of a stack, and the derived 
    classes deal with presentation.

    The stack knows what cards it contains, but the card does not know which stack it is in.

    '''
    def __init__(self):
        # Bottom card is self[0]; top is self[-1]
        super().__init__()

    def add(self, card):
        self.append(card)

    def isEmpty(self):
        return not self

    def clear(self):
        self[:] = []  

    def find(self, code):
        '''
        If the card with the given stack is in the stack,
        return its index.  If not, return -1.
        '''
        for idx, card in enumerate(self):
            if card.code == code:
                return idx
        return -1

class SelectableStack(Stack):
    '''
    A stack from which cards can be chosen, if they are in sequence,
    from the top of the stack. 
    '''
    def __init__(self):
        super().__init__()

    def grab(self, n):
        '''
        Remove the card at index k and all those on top of it.
        '''    
        answer = self[k:]
        self = self[:k]
        return answer

    def replace(self, cards):
        '''
        Move aborted.  Replace these cards on the stack.
        '''
        self.extend(cards)
        self.moving = None

    def canSelect(self, idx):
        if idx >= len(self):
            return False
        if not Card.isSequential(self[idx:]):
            return False
        return True
    
class OneWayStack(Stack):
    '''
    Used for the foundations.
    No cards can be selected.
    '''
    def __init__(self, suit):
        super().__init__()
        self.suit=suit

    def add(self, card):
        super().add(card)

class Card:
    '''
    A card is identified by its suit and rank.
    '''
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.color = 0 if suit in ('heart', 'diamond') else 1
        self.code = 13*SUITNAMES.index(suit)+rank-1  

    def goesOn(self, other):
        '''
        Can self be placed on other in a tableau pile?
        '''
        if self.color == other.color:
            return False
        answer = self.rank == other.rank-1 
        return answer
    
    def follows(self, other):
        return self.suit == other.suit and self.rank == other.rank+1

    def __repr__(self):
        return '%s %s'%(self.suit, RANKNAMES[self.rank])

    def __str__(self):
        return  '%s %s'%(self.suit, RANKNAMES[self.rank])

    @staticmethod
    def isSequential(seq):
        '''
        Are the cards in a descending sequence of alternating colors?
        '''
        answer =  all(map(lambda x, y: x.goesOn(y), seq[1:], seq))  
        return answer

class Model:
    '''
    The cards are all in self.deck, and are copied into the tableau piles
    All entries on the undo and redo stacks are in the form (source, target, n, f), where
        tableau piles are numbered 0 to 9 and foundations 10 to 17, 
        n is the number of cards moved, 
        f is a boolean indicating whether or not the top card of the source stack is flipped,
        except that the entry (0, 0, 10, 0) connotes dealing a row of cards. 
      '''
    def __init__(self):
        random.seed()
        self.deck = []
        self.selection = []
        self.undoStack = []
        self.redoStack = []
        self.createCards()
        self.foundations = []
        self.cells = [ ] 
        for k in range(4):
            self.foundations.append(OneWayStack(SUITNAMES[k]))
        self.tableau = []
        for k in range(8):
            self.tableau.append(SelectableStack()) 
        for k in range(4):
            self.cells.append(SelectableStack())
        self.grabPiles = self.tableau + self.cells
        self.piles = self.grabPiles + self.foundations
        self.deal()

    def shuffle(self):
        for f in self.foundations:
            f.clear()
        for w in self.tableau:
            w.clear()
        for c in self.cells:
            c.clear()
        random.shuffle(self.deck)

    def createCards(self):
        for rank, suit in itertools.product(ALLRANKS, SUITNAMES):
            self.deck.append(Card(rank, suit))

    def deal(self):
        self.shuffle()
        for n, card in enumerate(self.deck):
            self.tableau[n%8].add(card)
        self.undoStack = []
        self.redoStack = []    

    def gameWon(self):
        '''
        The game is won when all foundation piles are full
        '''
        return all(len(f)==13 for f in self.foundations) 

    def grab(self, k, idx):
        '''
        Initiate a move between tableau 
        Grab card idx and those on top of it from grabPiles[k] 
        Return a code numbers of the selected cards.
        We need to remember the data, since the move may fail.
        '''
        pile = self.grabPiles[k]
        if not pile.canSelect(idx):
            return []
        self.moveOrigin = k
        self.moveIndex = idx
        self.selection = pile[idx:]
        return self.selection

    def abortMove(self):
        self.selection = []

    def moving(self):
        return self.selection != [] 

    def getSelected(self):
        return self.selection

    def canDrop(self, idx):
        '''
        Can the moving cards be dropped on  self.piles[idx]?
        '''
        source = self.selection
        tableau = self.tableau
        cells = self.cells
        foundations = self.foundations
        piles = self.piles
        pile = piles[idx]

        if not source:
            return False
        if idx< 8:  # tableau pile
            # Note the super moves
            freeCells = len([f for f in cells if f.isEmpty()])
            #freeTableau = len([t for t in tableau if t.isEmpty() and t != pile])
            freeTableau = len([k for k in range(8) if k!=idx and piles[k].isEmpty()])
            maxMove = (1+freeCells)*2**freeTableau
            if len(source)> maxMove:
                return False
            if pile.isEmpty():
                return True
            return source[0].goesOn(pile[-1])
        
        elif idx < 12: # cell
            return len(source) == 1 and pile.isEmpty()
        
        else:    # foundation
            if len(source) != 1:
                return False
            if pile.isEmpty():
                return source[0].rank == ACE and source[0].suit==piles[idx].suit
            return source[0].follows(pile[-1])
        
    def completeMove(self, dest):
        '''
        Compete a legal move.
        Tranfer the moving cards to the destination stack.
        '''
        source = self.piles[self.moveOrigin]
        moving = self.selection
        target = self.piles[dest] 
        target.extend(self.selection)
        source[:] = source[:self.moveIndex]
        self.selection = []
        self.redoStack = []

    def firstFoundation(self):
        # return index of first empty foundation pile

        for i, f in enumerate(self.foundations):
            if f.isEmpty(): return i     

    def win(self):
        return all((len(f)  == 13 for f in self.foundations)) 

    def undo(self):
        ''''
        Pop a record off the undo stack and undo the corresponding move.
        '''
        (s, t, n, f) = self.undoStack.pop()
        self.redoStack.append((s,t,n, f))
        if (s, t, n, f) == DEAL:
            self.undeal()
        else:
            if f:   # flip top card
                self.tableau[s][-1].showBack()
            source = self.tableau[s] if s < 10 else self.foundations[s-10]
            target = self.tableau[t] if t < 10 else self.foundations[t-10]
            assert len(target) >= n
            source.extend(target[-n:])
            target[:] = target[:-n]

    def redo(self):
        ''''
        Pop a record off the redo stack and redo the corresponding move.
        ''' 
        (s, t, n, f) = self.redoStack.pop()
        self.undoStack.append((s,t,n, f))
        if (s, t, n, f) == DEAL:
            self.dealUp(True) 
        else:
            source = self.tableau[s] if s < 10 else self.foundations[s-10]
            target = self.tableau[t] if t < 10 else self.foundations[t-10]
            assert n <= len(source)
            target.extend(source[-n:])
            source[:] = source[:-n]     

    def canUndo(self):
        return self.undoStack != []

    def canRedo(self):
        return self.redoStack != []  

    def restart(self):
        while self.canUndo():
            self.undo()


            
            
