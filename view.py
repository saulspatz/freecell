# view.py
'''
The visual interface for free cell solitaire.
The view knows about the model, but not vice versa
The canvas widget is used for both view and controller.
'''
import sys, os, itertools, time
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
from model import SUIT_NAMES, RANK_NAMES, ALLRANKS, SUIT_SYMBOLS, Card

# Constants determining the size and layout of cards and stacks.  
#CARDWIDTH = 75   Constants used with small deck
#CARDHEIGHT = 113
#OFFSET = 20

CARDWIDTH = 85
CARDHEIGHT = 128
OFFSET = 23
MARGIN = 10
XSPACING1 = CARDWIDTH + 2*MARGIN
XSPACING2 = CARDWIDTH + 3*MARGIN
FILLER = 7*MARGIN
YSPACING = CARDHEIGHT + 4*MARGIN


BACKGROUND = '#070'
PILEFILL = 'OliveDrab4' # fill color of piles
TEXT = 'yellow'              # button text color
BUTTON = 'forest green'

# Cursors
DEFAULT_CURSOR = 'arrow'
SELECT_CURSOR = 'hand2'

SUIT_FONT=("Times", "48", "bold")

imageDict = {}   # hang on to images, or they may disappear!

class ButtonBar(tk.Canvas):
    def __init__(self, parent):
        tk.Canvas.__init__(self,parent, bg=BACKGROUND, bd=0, highlightthickness=0)
        self.configure(height=5*MARGIN,width=6*XSPACING2)
        width=int(self['width'])
        self.makeButton(width//2-12*MARGIN, 'undo')
        self.makeButton(width//2-4*MARGIN, 'redo')
        self.makeButton(width//2+4*MARGIN, 'restart')
        self.place(in_=parent, relx=.5,y=0,anchor=tk.N)    

    def makeButton(self, left, text):
        self.create_oval(left, MARGIN, left+6*MARGIN, 4*MARGIN, fill=BUTTON, outline=BUTTON, tag = text)
        self.create_text(left+3*MARGIN,2.5*MARGIN,text=text.title(),fill=TEXT,tag=text,anchor=tk.CENTER)

class View: 
    '''
    Cards are represented as canvas image iitems,  displaying either the face
    or the back as appropriate.  Each card has the tag "card".  This is 
    crucial, since only canvas items tagged "card" will respond to mouse
    clicks.
    '''
    def __init__(self, parent, quit, **kwargs):
        # quit is function to call when main window is closed
        self.parent = parent          # parent is the Free Cell application
        self.model =  parent.model
        self.root = root = tk.Tk()
        root.protocol('WM_DELETE_WINDOW', quit)
        width = 5*MARGIN+8*XSPACING2
        self.root.wm_geometry('%dx850-10+10'%width)
        root.title("Free Cell Solitaire")

        root.minsize(width=width, height=500)
        root.maxsize(width=width, height=2500)
        self.menu = tk.Menu(root)         # parent constructs actual menu         
        root.config(menu=self.menu)                 
        self.tableau = []           # NW corners of the tableau piles
        self.foundations = []   # NW corners of the foundation piles
        self.cells=[]                 #NW corners of the free cells
        x = 4*MARGIN
        y = 6* MARGIN
        for k in range(4):
            self.cells.append((x, y))
            x += XSPACING1
        x += FILLER
        for k in range(4):
            self.foundations.append((x, y))
            x += XSPACING1
        y += YSPACING
        x = 4*MARGIN
        for k in range(8):
            self.tableau.append((x, y)) 
            x += XSPACING2 
        self.grabPiles = self.tableau+self.cells
        self.piles = self.grabPiles+self.foundations        
        canvas = self.canvas = tk.Canvas(root, bg=BACKGROUND, cursor=DEFAULT_CURSOR, 
                                                             bd=0, highlightthickness=0, **kwargs)
        canvas.pack(expand=tk.YES, fill=tk.Y)
        width = kwargs['width']
        height = kwargs['height']

        self.loadImages()
        self.createCards()
        canvas.tag_bind("card", '<ButtonPress-1>', self.onClick)
        canvas.tag_bind("card", '<Double-Button-1>', self.onDoubleClick)
        canvas.bind('<B1-Motion>', self.drag)
        canvas.bind('<ButtonRelease-1>', self.onDrop)

        for t in self.tableau:
            canvas.create_rectangle(t[0], t[1], t[0]+CARDWIDTH, t[1]+CARDHEIGHT, 
                                                    fill=PILEFILL, outline=PILEFILL)    
        for idx, f in enumerate(self.foundations):
            canvas.create_rectangle(f[0], f[1], f[0]+CARDWIDTH, f[1]+CARDHEIGHT, 
                                                    fill=PILEFILL, outline=PILEFILL)
            canvas.create_text(f[0]+CARDWIDTH//2,f[1]+CARDHEIGHT//2, 
                                            text=SUIT_SYMBOLS[idx], fill='khaki',font=SUIT_FONT)
        for c in self.cells:
            canvas.create_rectangle(c[0], c[1], c[0]+CARDWIDTH, c[1]+CARDHEIGHT, 
                                                    fill=PILEFILL, outline=PILEFILL)
        
        self.buttons = ButtonBar(canvas)
        self.buttons.tag_bind('undo', '<ButtonPress-1>', self.undo)
        self.buttons.tag_bind('redo', '<ButtonPress-1>', self.redo)
        self.buttons.tag_bind('restart', '<ButtonPress-1>', self.restart)
        self.show()

    def start(self):
        self.root.mainloop()

    def loadImages(self):
        PhotoImage = tk.PhotoImage
        cardDir = os.path.join(os.path.dirname(sys.argv[0]), 'cards/large') 
        for suit, rank in itertools.product(SUIT_NAMES, ALLRANKS):
            face = PhotoImage(file = os.path.join(cardDir, RANK_NAMES[rank]+suit+'.gif'))               
            imageDict[rank, suit] = face

    def createCards(self):
        model = self.model
        canvas = self.canvas    
        for card in model.deck:
            c = canvas.create_image(-200, -200, image = None, anchor = tk.NW, tag = "card")
            canvas.addtag_withtag('code%s'%card.code, c)

    def showTableau(self, k):
        '''
        Display tableau pile number k
        '''
        x, y = self.tableau[k]
        canvas = self.canvas
        for card in self.model.tableau[k]:
            tag = 'code%s'%card.code
            canvas.coords(tag, x, y)
            foto = imageDict[card.rank, card.suit]
            y += OFFSET
            canvas.itemconfigure(tag, image = foto)
            canvas.tag_raise(tag) 
            
    def showCell(self, k):
        '''
        Display free cell number k
        '''
        x, y = self.cells[k]
        canvas = self.canvas
        for card in self.model.cells[k]:
            tag = 'code%s'%card.code
            canvas.coords(tag, x, y)
            foto = imageDict[card.rank, card.suit]
            canvas.itemconfigure(tag, image = foto)
            canvas.tag_raise(tag) 

    def show(self):
        model = self.model
        canvas = self.canvas
        for k in range(8):
            self.showTableau(k)
        for k in range(4):
            self.showFoundation(k)
        for k in range(4):
            self.showCell(k)
        if model.canUndo():
            self.enableUndo()
        else:
            self.disableUndo()
        if model.canRedo():
            self.enableRedo()
        else:
            self.disableRedo()   

    def dealUp(self):
        self.model.dealUp()
        self.show()

    def showFoundation(self, k):
        model = self.model
        canvas = self.canvas
        x, y = self.foundations[k]
        for card in model.foundations[k]:
            tag = 'code%s'%card.code
            canvas.itemconfigure(tag, image = imageDict[card.rank, card.suit])
            canvas.coords(tag,x,y)
            canvas.tag_raise(tag)

    def grab(self, selection, k, mouseX, mouseY):
        '''
        Grab the cards in selection.
        k is the index of the source grabPile.
        '''
        canvas = self.canvas
        if not selection:
            return
        self.mouseX, self.mouseY = mouseX, mouseY
        west = self.grabPiles[k][0]
        for card in selection:
            tag = 'code%s'%card.code
            canvas.tag_raise(tag)
            canvas.addtag_withtag("floating", tag)
        canvas.configure(cursor=SELECT_CURSOR)
        dx = 5 if mouseX - west > 10 else -5
        canvas.move('floating', dx, 0)

    def drag(self, event):
        canvas = self.canvas
        try:
            x, y = event.x, event.y
            dx, dy = x - self.mouseX, y - self.mouseY
            self.mouseX, self.mouseY = x, y
            canvas.move('floating', dx, dy)
        except AttributeError:
            pass

    def onClick(self, event):
        '''
        Respond to click on cell or tableau pile.  
        Clicks on foundation piles are ignored.
        '''
        model = self.model
        canvas = self.canvas
        tag = [t for t in canvas.gettags('current') if t.startswith('code')][0]
        code = tag[4:]             # code of the card clicked
        for k, p in enumerate(model.grabPiles):
            idx = p.find(code)
            if idx != -1:
                break
        else:       # loop else
            return
        selection = model.grab(k, idx)
        self.grab(selection, k, event.x, event.y)

    def onDoubleClick(self, event):
        model = self.model
        canvas = self.canvas
        tag = [t for t in canvas.gettags('current') if t.startswith('code')][0]
        code = tag[4:]             # code of the card clicked
        for k,p in enumerate(model.tableau):
            try:
                if p[-1].code == code:
                    break
            except IndexError:
                pass
        else:    #loop else
            return
        if model.topToCell(k):
            self.show()
            self.automaticMoves()
    
    def dropTargets(self):
        piles = self.piles
        heaps = self.model.piles
        targets = [[left, top, left+CARDWIDTH, top+CARDHEIGHT ] for left,top in piles]
        for idx in range(8):
            cards = len(heaps)
            if cards > 1:
                targets[idx][3]+= OFFSET * (cards-1)
        return targets    

    def overlappingPiles(self):
        '''
        Return a list of the indices of the piles that overlap the cards being moved, 
        sorted in decreasing order of overlap
        '''
        model = self.model
        origin = model.moveOrigin
        piles = self.piles
        targets = self.dropTargets()
        answer = [ ]
        west, north, east, south = self.canvas.bbox(tk.CURRENT)
        dragging = len(model.selection)
        if dragging > 1:
            south += OFFSET *(dragging-1)
        for idx in range(16):
            if idx == origin: continue
            left, top, right, bottom = targets[idx]
            horizontal = min(east, right) - max(west, left) 
            if horizontal <= 0: continue
            vertical = min(bottom, south) -  max(top, north)
            if vertical <= 0: continue
            answer.append((horizontal*vertical, idx))
        return [ans[1] for ans in sorted(answer, reverse=True)]
                    
    def onDrop(self, event):
        '''
        Drop the selected cards.    The  cards being dragged must overlap the target pile.  
        If they overlap more than one pile, all such piles are tested, in order of the 
        area overlapped.
        '''
        piles = self.piles
        model = self.model
        canvas = self.canvas   
        if model.selection == [ ]:
            return
        x, y = event.x, event.y
        canvas.configure(cursor=DEFAULT_CURSOR)
        success = False
        for idx in self.overlappingPiles():
                if not model.piles[idx].canDrop():
                    continue
                self.completeMove(idx)
                success = True
                break 
        if not success:  
            self.abortMove()
        self.show()

    def abortMove(self):
        canvas = self.canvas
        self.model.abortMove()
        self.show()
        canvas.dtag('floating')

    def completeMove(self, dest):
        model = self.model
        model.completeMove(dest)
        self.show()
        self.canvas.dtag('floating')
        self.automaticMoves()
            
    def automaticMoves(self):
        while self.model.automaticMove():
            self.show()
            self.canvas.update_idletasks()
            time.sleep(.06)        

    def undo(self, event):
        self.model.undo()
        self.show()

    def redo(self, event):
        self.model.redo()
        self.show()  

    def restart(self, event):
        self.model.restart()
        self.show()

    def disableRedo(self):
        self.buttons.itemconfigure('redo', state=tk.HIDDEN)

    def disableUndo(self):
        for item in ('undo', 'restart'):
            self.buttons.itemconfigure(item, state=tk.HIDDEN)

    def enableRedo(self):
        self.buttons.itemconfigure('redo', state=tk.NORMAL)

    def enableUndo(self):
        for item in ('undo', 'restart'):
            self.buttons.itemconfigure(item, state=tk.NORMAL)

    def wm_delete_window(self):
        self.root.destroy()

    def done(self, num):
        self.root.destroy()    
