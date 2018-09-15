# model.py Model for free cell solitaire

import random, itertools
from collections import namedtuple

UndoRecord = namedtuple('Undorecord', 'source target cards auto'.split())

ACE = 1
JACK = 11
QUEEN = 12
KING = 13
ALLRANKS = range(1, 14)      # one more than the highest value

# RANKNAMES is a list that maps a rank to a string.  It contains a
# dummy element at index 0 so it can be indexed directly with the card
# value.

SUIT_NAMES = 'SHDC'
RANK_NAMES = ' A23456789TJQK'
SUIT_SYMBOLS= ('\u2660','\u2665','\u2666','\u2663') 

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
        If the card with the given code is in the stack,
        return its index.  If not, return -1.
        '''
        for idx, card in enumerate(self):
            if card.code == code:
                return idx
        return -1
    
    def grab(self, n):
        '''
        Remove the card at index k and all those on top of it.
        '''    
        answer = self[k:]
        self = self[:k]
        return answer
    
    def canDrop(self):
        raise NotImplementedError
    
    def canSelect(self, idx):
        raise NotImplementedError

class TableauPile(Stack):
    def __init__(self):
        super().__init__()
        
    def canSelect(self, idx):
        if idx >= len(self):
            return False
        for card1, card2 in zip(self[idx:], self[idx+1:]):
            if card1.color == card2.color:
                return False
            if card2.rank != card1.rank-1:
                return False
        return True
    
    def canDrop(self):
        '''Can the moving cards be dropped here?'''
        source = model.selection
        tableau = model.tableau
        cells = model.cells
        freeCells = len([c for c in cells if c.isEmpty()])
        freeTableau = len([t for t in tableau if t.isEmpty()])
        if self.isEmpty(): freeTableau -= 1
        maxMove = (1+freeCells)*2**freeTableau
        if len(source)> maxMove:
            return False
        if self.isEmpty():
            return True
        lower = source[0]
        upper = self[-1]
        if lower.color == upper.color:
            return False
        return lower.rank == upper.rank-1        
          
class Cell(Stack):
    def __init__(self):
        super().__init__()
    
    def canSelect(self, idx):
        return True
    
    def canDrop(self):
        '''Can the moving cards be dropped here?'''
        return self.isEmpty() and len(model.selection)==1
    
class FoundationPile(Stack):
    '''
    Used for the foundations.
    No cards can be selected.
    '''
    def __init__(self, suit):
        super().__init__()
        self.suit=suit

    def add(self, card):
        super().add(card)
        
    def canSelect(self, idx):
        return False
    
    def canDrop(self):
        '''Can the moving cards be dropped here?'''
        source = model.selection
        if len(source) != 1:
            return False
        card = source[0]
        if card.suit != self.suit:
            return False
        if self.isEmpty():
            return card.rank == ACE
        return card.rank-1 == self[-1].rank

def cardCode(rank, suit):
    return RANK_NAMES[rank]+suit

class Card:
    '''
    A card is identified by its suit and rank.
    '''
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.color = 0 if suit in 'HD' else 1
        self.code =cardCode(rank, suit)

    def __repr__(self):
        return self.code

    def __str__(self):
        r = RANK_NAMES[self.rank]
        s = SUIT_SYMBOLS[SUIT_NAMES.index(self.suit)]
        return r+s

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
            self.foundations.append(FoundationPile(SUIT_NAMES[k]))
        self.tableau = []
        for k in range(8):
            self.tableau.append(TableauPile()) 
        for k in range(4):
            self.cells.append(Cell())
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
        for rank, suit in itertools.product(ALLRANKS, SUIT_NAMES):
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

    def completeMove(self, dest):
        '''
        Compete a legal move.
        Tranfer the moving cards to the destination stack.
        '''
        src = self.moveOrigin
        source = self.piles[src]
        select = self.selection
        target = self.piles[dest] 
        target.extend(self.selection)
        source[:] = source[:self.moveIndex]
        self.undoStack.append(UndoRecord(src, dest, len(select), False))
        self.selection = []
        self.redoStack = []

    def win(self):
        return all((len(f)  == 13 for f in self.foundations)) 
    
    def topToCell(self, idx):
        '''
        Move the top card of piles[idx] to a free cell
        '''
        piles = self.piles
        for k in range(8,12):
            if piles[k].isEmpty():
                break
        else:   # loop else
            return False
        piles[k].append(piles[idx].pop())
        self.undoStack.append(UndoRecord(idx, k, 1, False))
        return True

    def undo(self):
        ''''
        Pop any automatic moves off the stack and redo the corresponding moves.
        Then pop one record off the undo stack and undo the corresponding move.
        
        '''
        def unplay():
            (s, t, n, a) = record =  undoStack.pop()
            redoStack.append(record)
            source = piles[s] 
            target = piles[t]
            source.extend(target[-n:])
            target[:] = target[:-n]            
            
        undoStack = self.undoStack
        redoStack = self.redoStack
        piles = self.piles
        while undoStack[-1].auto : 
            unplay()
        unplay()

    def redo(self):
        ''''
        Pop a record off the redo stack and redo the corresponding move.
        Then pop and redo any automatic moves.
        ''' 
        def replay():
            (s, t, n, a) = record = redoStack.pop()
            undoStack.append(record)
            source = piles[s] 
            target = piles[t]
            target.extend(source[-n:])
            source[:] = source[:-n]             
            
        undoStack = self.undoStack
        redoStack = self.redoStack
        piles = self.piles        
        replay()
        try:
            while redoStack[-1].auto:
                replay()
        except IndexError:
            pass
            
    def canUndo(self):
        return self.undoStack != []

    def canRedo(self):
        return self.redoStack != []  

    def restart(self):
        while self.canUndo():
            self.undo()

    def automaticMove(self):
        piles = self.piles
        foundations = self.foundations
        reds = piles[13], piles[14]     # foundations
        blacks = piles[12], piles[15]
        for idx in range(12):
            add = False
            source = piles[idx]
            if source.isEmpty(): continue
            card = source[-1]
            target =piles[ 12 + SUIT_NAMES.index(card.suit)]
            if card.rank == ACE:
                add = True
            elif card.rank == 2:
                add =  not target.isEmpty()
            else:
                if len(target) != card.rank-1: 
                    continue
                stacks = blacks if card.suit in 'HD' else reds
                if all(len(stack)>=card.rank-1 for stack in stacks):
                    add = True
                elif all(len(fnd)>=card.rank-2 for fnd in foundations):
                    add = True
            if add:
                target.add(source.pop())
                self.undoStack.append(UndoRecord(idx,piles.index(target),1,True))
                break
        return add
                          
model = Model()