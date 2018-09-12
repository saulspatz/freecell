# view.py
'''
The visual interface for free cell solitaire.
The view knows about the model, but not vice versa
The canvas widget is used for both view and controller.
'''
import sys, os, itertools
import tkinter as tk
from model import SUITNAMES, RANKNAMES, ALLRANKS, Card

# Constants determining the size and layout of cards and stacks.  

CARDWIDTH = 75
CARDHEIGHT = 113
MARGIN = 10
XSPACING1 = CARDWIDTH + 2*MARGIN
XSPACING2 = CARDWIDTH + 3*MARGIN
FILLER = 7*MARGIN
YSPACING = CARDHEIGHT + 4*MARGIN
OFFSET = 20

BACKGROUND = '#070'
OUTLINE = '#060'        # outline color of foundation files
TEXT = 'yellow'              # button text color
BUTTON = 'forest green'

# Cursors
DEFAULT_CURSOR = 'arrow'
SELECT_CURSOR = 'hand2'

imageDict = {}   # hang on to images, or they may disappear!

class ButtonBar(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg=BACKGROUND, bd=0, highlightthickness=0)
        self.configure(height=5*MARGIN,width=6*XSPACING2,bg='gray')
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
        width = 4*MARGIN+8*XSPACING2
        self.root.wm_geometry('%dx850-10+10'%width)
        root.title("Free Cell Solitaire")

        root.minsize(width=width, height=500)
        root.maxsize(width=width, height=2500)
        self.menu = tk.Menu(root)         # parent constructs actual menu         
        root.config(menu=self.menu)                 
        self.tableau = []           # NW corners of the tableau piles
        self.foundations = []   # NW corners of the foundation piles
        self.cells=[]                 #NW corners of the free cells
        x = 2*MARGIN
        y = 6* MARGIN
        for k in range(4):
            self.cells.append((x, y))
            x += XSPACING1
        x += FILLER
        for k in range(4):
            self.foundations.append((x, y))
            x += XSPACING1
        y += YSPACING
        x = 2*MARGIN
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
            canvas.create_rectangle(t[0], t[1], t[0]+CARDWIDTH, t[1]+CARDHEIGHT, outline = OUTLINE)    
        for f in self.foundations:
            canvas.create_rectangle(f[0], f[1], f[0]+CARDWIDTH, f[1]+CARDHEIGHT, outline = OUTLINE)
        for c in self.cells:
            canvas.create_rectangle(c[0], c[1], c[0]+CARDWIDTH, c[1]+CARDHEIGHT, outline = OUTLINE)
        self.buttons = ButtonBar(canvas)
        self.buttons.tag_bind('undo', '<ButtonPress-1>', self.undo)
        self.buttons.tag_bind('redo', '<ButtonPress-1>', self.redo)
        self.buttons.tag_bind('restart', '<ButtonPress-1>', self.restart)
        self.show()

    def start(self):
        self.root.mainloop()

    def loadImages(self):
        PhotoImage = tk.PhotoImage
        cardDir = os.path.join(os.path.dirname(sys.argv[0]), 'cards') 
        for rank, suit in itertools.product(ALLRANKS, SUITNAMES):
            face = PhotoImage(file = os.path.join(cardDir, suit+RANKNAMES[rank]+'.gif'))               
            imageDict[rank, suit] = face

    def createCards(self):
        model = self.model
        canvas = self.canvas    
        for card in model.deck:
            c = canvas.create_image(-200, -200, image = None, anchor = tk.NW, tag = "card")
            canvas.addtag_withtag('code%d'%card.code, c)

    def showTableau(self, k):
        '''
        Display tableau pile number k
        '''
        x, y = self.tableau[k]
        canvas = self.canvas
        for card in self.model.tableau[k]:
            tag = 'code%d'%card.code
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
            tag = 'code%d'%card.code
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
        if model.win():
            canvas.yview_moveto(0.0)

    def dealUp(self):
        self.model.dealUp()
        self.show()

    def showFoundation(self, k):
        model = self.model
        canvas = self.canvas
        x, y = self.foundations[k]
        for card in model.foundations[k]:
            tag = 'code%d'%card.code
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
        self.yfraction = canvas.yview()[0]
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
        code = int(tag[4:])             # code of the card clicked
        for k, p in enumerate(model.grabPiles):
            idx = p.find(code)
            if idx != -1:
                break
        else:       # loop else
            return
        selection = model.grab(k, idx)
        self.grab(selection, k, event.x, event.y)

    def onDoubleClick(self, event):
        pass

    def horizontalOverlap(self, w1, e1, w2, e2):
        '''
        Find the horizontal overlap between two rectangles with west and east edges
        (w1, e1) and (w2, e2) respectively.  A negative number is returned if they
        don't overlap at all.  A return value of 0 means they coincide in one edge only.
        Vertical position of the rectangles is ignored, so they may be considered infinite
        strips.
        '''
        return min(e1, e2) - max(w1, w2)

    def findOverlapping(self, seq, west, east):
        '''
        Return a list of the indices of the piles in seq that overlap a card with edges
        west and east, sorted in decreasing order of overlap
        '''
        def overlap(pile):
            return self.horizontalOverlap(west, east, pile[0], pile[0]+CARDWIDTH)
        answer = [(pile, k) for k, pile in enumerate(seq) if  overlap(pile)>= 0]
        answer = sorted(answer, key = lambda x: overlap(x[0]), reverse=True)
        return [x[1] for x in answer]

    def onDrop(self, event):
        '''
        Drop the selected cards.  The cards being dragged must overlap a tableau pile.
        If they overlap two tableau piles, the one with more overlap is tested first.  
        If that is not a legal drop target then the other pile is considered.
        '''
        piles = self.piles
        model = self.model
        canvas = self.canvas   
        if not model.moving():
            return
        canvas.configure(cursor=DEFAULT_CURSOR)
        west, north, east, south = canvas.bbox(tk.CURRENT)
        success = False

        for idx in self.findOverlapping(piles, west, east):
            if idx == model.moveOrigin or not model.canDrop(idx):
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
        canvas.yview_moveto(self.yfraction)
        self.showTableau(self.model.moveOrigin)
        canvas.dtag('floating', 'floating')

    def completeMove(self, dest):
        model = self.model
        model.completeMove(dest)
        self.show()
        self.canvas.dtag('floating', 'floating')

    def undo(self, event):
        self.model.undo()
        self.show()

    def redo(self, event):
        self.model.redo()
        self.show()  

    def restart(self, event):
        self.model.restart()
        self.show()

    def redeal(self, event):
        self.model.redeal()
        self.show()

    def disableRedo(self):
        self.buttons.itemconfigure('redo', state=tk.HIDDEN)

    def disableUndo(self):
        for item in ('undo', 'restart', 'redeal'):
            self.buttons.itemconfigure(item, state=tk.HIDDEN)

    def enableRedo(self):
        self.buttons.itemconfigure('redo', state=tk.NORMAL)

    def enableUndo(self):
        for item in ('undo', 'restart', 'redeal'):
            self.buttons.itemconfigure(item, state=tk.NORMAL)

    def wm_delete_window(self):
        self.root.destroy()

    def done(self, num):
        self.root.destroy()    
