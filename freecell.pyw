# freecell.pyw

'''
Free cell solitaire.  I wrote this because the games I find online have various deficiencies. 
The cards are too small, and they don't leave enough space between the free cells
and the foundation piles.  Also, they don't include solvers.  A free cell solver is
challenging, but I'll try iterative deepening.
'''
import model
from view import View
import tkinter as tk
from tkinter.messagebox import showerror, showinfo, askokcancel
import sys, os

helpText = '''
OBJECTIVE
Free cell is played with a deck of 52 cards.\
The objective is to arrange each of the four suits in sequence \
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
  
The tableau piles are built downward in alteranting colors, so a red Jack \
may be placed on top of a black Queen, but not on top of a red \
Queen.  An Ace can be moved to an empty foudation pile.
  
Any card can be moved to an empty free cell, to an empty tableau pile.

The foundation piles are built upward by suit.
   
According to the rules, only one card can be moved at a time, but this is \
tedious, so the programs allows moving multiple cards at once, if this can \
be accomplished by making use of empty free cells and tableau piles.

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
        self.model = model.model
        self.view = View(self, self.quit, width=1000, height=1000, scrollregion=(0, 0, 950, 3000) )
        self.makeHelp()
        self.makeMenu()
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
        top.title("Free Cell Help")
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

        game = tk.Menu(top, tearoff=False)
        game.add_command(label='New', command=self.deal)
        game.add_command(label='Help', command = self.showHelp)  
        game.add_command(label='Quit', command=self.quit)
        top.add_cascade(label='Game', menu=game)

    def notdone(self):
        showerror('Not implemented', 'Not yet available') 

    def showHelp(self):
        self.helpText.deiconify()
        self.helpText.text.see('1.0')  

    def quit(self):
        self.view.root.quit()

if __name__ == "__main__":
    FreeCell()
