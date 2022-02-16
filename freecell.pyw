# freecell.pyw

'''
Freecell solitaire.  I wrote this because the games I find online have various deficiencies. 
The cards are too small, and they don't leave enough space between the freecells
and the foundation piles.  Also, they don't include solvers. 
'''
import model
from view import View

import tkinter as tk
from tkinter.messagebox import showerror, showinfo, askokcancel
import sys, os

helpText = '''
This program implements three variants related solitaire (patience) games: \
freecell, forecell, and Baker's game.  The games differ only \
in the rules for moving cards.

OBJECTIVE
All three games  are played with a deck of 52 cards.\
The objective in each game is to arrange each of the four suits in sequence \
from the Ace to the King on the foundations piles.\
If all suits have been built on the foundations, the game is won.

SETUP
There are eight tableau piles.\
The leftmost four initially have seven cards each, and the others \
initially have six cards each.   There are also four foundation piles \
and four free cells, initially empty.  

MOVING CARDS
The cards in the free cells and the top cards of the tableau piles \
are available for play.  Cards in the foundation piles cannot be moved.
  
The tableau piles in freecell and forecell  are built downward in alternating \
colors, so a red Jack may be placed on top of a black Queen, but not on top of \
a red Queen.  In Baker's game, the cards are built downward by suit, so the |
Jack of Spades may be placed on top of the Queen of Spades, but on no other Queen.

An Ace can be moved to an empty foundation pile  in all the games.
  
Any card can be moved to an empty free cell. 

In freecell and Baker's game, any card may be moved to an empty tableau pile. \
but in forecell, only a King may be played to an empty foundation pile.
   
According to the rules, only one card can be moved at a time, but this is \
tedious, so the programs allows moving multiple cards at once, if this can \
be accomplished by making use of empty free cells and tableau piles.

As the play proceeds, there are situations when there is no point in not playing \
some card to the foundation piles.  For example, an Ace should always be played \
to the foundations, because it is of no use in the tableau or the cells.  The \
program detects such situations and plays any such cards automatically, \
except at the very beginning of the game.

BUTTONS
The "Undo" and Redo" buttons are self-explanatory.  \
The "Restart" button puts the game back to the beginning, but you can \
still redo all your moves. 

DOUBLE-CLICK
Double-clicking the top card of a tableau pile will move it to a free cell, \
if there is one available.
'''        
class FreeCell:
    def __init__(self):
        os.environ['FREECELL_SOLVER_QUIET']='1'
        cwd = os.getcwd()
        progDir= os.path.dirname(sys.argv[0])
        self.runDir = os.path.join(cwd, progDir)         
        self.model = model.model
        self.model.parent = self
        self.view = View(self, self.quit, width=1000, height=1000, scrollregion=(0, 0, 950, 3000) )
        self.gameType = tk.IntVar()
        self.gameType.set(0)            
        self.makeHelp()
        self.makeMenu()
        self.gameType.trace('w', self.optionChanged)       
        self.view.start()      #  start the event loop

    def deal(self):
        model = self.model
        model.deal()
        self.view.show()

    def makeHelp(self):
        top = self.helpText = tk.Toplevel()
        top.transient(self.view.root)
        top.protocol("WM_DELETE_WINDOW", top.withdraw)
        top.withdraw()
        top.title("Solitaire Help")
        f = tk.Frame(top)
        self.helpText.text = text = tk.Text(f, height=30, width = 80, wrap=tk.WORD)
        text['font'] = ('helevetica', 14, 'normal')
        text['bg'] = '#ffef85'
        text['fg'] = '#8e773f'
        scrollY = tk.Scrollbar(f, orient=tk.VERTICAL, command=text.yview)
        text['yscrollcommand'] = scrollY.set
        text.grid(row=0, column=0, sticky='NSEW')
        f.rowconfigure(0, weight=1)
        f.columnconfigure(0, weight=1)
        scrollY.grid(row=0, column=1, sticky='NS')
        tk.Button(f, text='Dismiss', command=top.withdraw).grid(row=1, column=0)
        f.grid(sticky='NSEW')
        top.rowconfigure(0, weight=1)
        text.insert(tk.INSERT,helpText)

    def makeMenu(self):
        top = self.view.menu
        gameVar = self.gameType

        game = tk.Menu(top, tearoff=False)
        game.add_command(label='New', command=self.deal)
        game.add_command(label='Help', command = self.showHelp)  
        game.add_command(label='Quit', command=self.quit)
        top.add_cascade(label='Game', menu=game)
        
        options = tk.Menu(top, tearoff=False)
        options.add_radiobutton(label='Freecell', variable=gameVar, value=0)
        options.add_radiobutton(label='Forecell',  variable=gameVar, value=1)
        options.add_radiobutton(label="Baker's Game",  variable=gameVar, value=2)
        top.add_cascade(label='Options', menu=options)        

    def showHelp(self):
        self.helpText.deiconify()
        self.helpText.text.see('1.0')  
        
    def optionChanged(self, *args):
        model = self.model
        titles = ['Freecell Solitaire',
                       'Forecell Solitaire',
                       "Baker's Game"]
        try:        
            game = model.gameType
            title = titles[game]
            showinfo(title, 'Game change will take effect next deal', 
                        parent=self.view.canvas)
        except AttributeError:
            game = self.gameType.get()
            self.view.root.title(titles[game])
            
    def quit(self):
        try:
            self.model.solverProc.kill()
        except:
            pass
        self.view.root.quit()

if __name__ == "__main__":
    FreeCell()
