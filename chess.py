

from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import TextNode
from panda3d.core import LPoint3, LVector3, BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from enum import Enum
import sys

BLACK = (0, 0, 0, 1)
WHITE = (1, 1, 1, 1)
HIGHLIGHT_POSITIVE = (0.498039, 1, 0, 1)
HIGHLIGHT_NEGATIVE = (1, 0, 0, 1)
PIECEBLACK = (.15, .15, .15, 1)

check = None

def PointAtZ(z, point, vec):
    return point + vec * ((z - point.getZ()) / vec.getZ())

def SquarePos(i):
    return LPoint3((i % 8) - 3.5, int(i // 8) - 3.5, 0)

def trash():
    return LPoint3(-500, -500)

def SquareColor(i):
    if (i + ((i // 8) % 2)) % 2:
        return BLACK
    else:
        return WHITE

class ChessboardDemo(ShowBase):

    def calculatePossiblePositions(self, startingPos, movementArray):
        possibleIndexes = []
        multiplierArray = [[7, 8, 9], [-1, 1], [-9, -8, -7]]
        for i in range(0,3):
            for j in range(0,3):
                if (i == 1 and j == 2):
                    continue
                for k in range(1,movementArray[i][j] + 1):
                    possibleIndex = startingPos + k * multiplierArray[i][j]
                    if possibleIndex < 64 and possibleIndex >= 0:
                        possibleIndexes.append(startingPos + k * multiplierArray[i][j])
        return list(set(possibleIndexes))


    def getAllCollidingPositions(self, startingPos, possibleEndPositions):
        collisions = []
        for possibleEndPosition in possibleEndPositions:
            if (not isinstance(self.pieces[possibleEndPosition], type(None))):
                if (self.pieces[possibleEndPosition].obj.getColor() == self.turn):
                    collisions.append(possibleEndPosition)
        return collisions

    def getDirectionMultiplier(self, startingPos, endPos):
        temp = endPos - startingPos
        if temp < 0:
            if temp % -8 == 0:
                return -8
            elif temp % -9 == 0:
                return -9
            elif temp % -7 == 0:
                return -7
            else:
                return -1
        else:
            if temp % 8 == 0:
                return 8
            elif temp % 7 == 0:
                return 7
            elif temp % 9 == 0:
                return 9
            else:
                return 1

        

    def checkCollisionInLine(self, startingPos, endPos, collidingPositions):
        if endPos in collidingPositions:
            return True
        else:
            directionalMultiplier = self.getDirectionMultiplier(startingPos, endPos)
            positionsOnTheLine = []
            temp = startingPos + directionalMultiplier
            while temp != endPos:
                positionsOnTheLine.append(temp)
                temp += directionalMultiplier

            for position in positionsOnTheLine:
                if (isinstance(self.pieces[position], Piece)):
                    return True
            return False


    def checkIfRoutePossible(self, startingPos, endPos, movementArray):
        if (isinstance(self.pieces[startingPos], Knight)):
            endPositions = []
            for i in movementArray:
                endPositions.append(startingPos + i)

            if endPos in endPositions:
                return True
            else:
                return False
        if (self.turn == PIECEBLACK and isinstance(self.movingPiece, Pawn)):
            movementArray = list(reversed(movementArray))
        listOfPossiblePositions = self.calculatePossiblePositions(startingPos, movementArray)
        #listOfPossiblePositions.remove(startingPos)
        listOfCollidingPositions = self.getAllCollidingPositions(startingPos, listOfPossiblePositions)
        if endPos in listOfPossiblePositions:
            if not self.checkCollisionInLine(startingPos, endPos, listOfCollidingPositions):
                return True

        return False





    def __init__(self):
        ShowBase.__init__(self)
        self.turn = WHITE
        self.movingPiece = None
        self.isMovementPossible = False

        self.escapeEvent = OnscreenText(
            text="ESC: Quit", parent=base.a2dTopLeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.1),
            align=TextNode.ALeft, scale = .05)
        self.mouse1Event = OnscreenText(
            text="Left-click and drag: Pick up and drag piece",
            parent=base.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.16), scale=.05)

        self.accept('escape', sys.exit)  # Escape quits
        self.disableMouse()  # Disble mouse camera control
        camera.setPosHpr(0, -12, 8, 0, -35, 0)
        self.setupLights()

        self.picker = CollisionTraverser()  # Make a traverser
        self.pq = CollisionHandlerQueue()  # Make a handler
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()  # Make our ray
        # Add it to the collision node
        self.pickerNode.addSolid(self.pickerRay)
        # Register the ray as something that can cause collisions
        self.picker.addCollider(self.pickerNP, self.pq)

        self.squareRoot = render.attachNewNode("squareRoot")
        # For each square
        self.squares = [None for i in range(64)]
        self.pieces = [None for i in range(64)]
        for i in range(64):
            # Load, parent, color, and position the model (a single square
            # polygon)
            self.squares[i] = loader.loadModel("models/square")
            self.squares[i].reparentTo(self.squareRoot)
            self.squares[i].setPos(SquarePos(i))
            self.squares[i].setColor(SquareColor(i))

            self.squares[i].find("**/polygon").node().setIntoCollideMask(
                BitMask32.bit(1))
            self.squares[i].find("**/polygon").node().setTag('square', str(i))

        pieceOrder = (Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook)

        for i in range(8, 16):
            # Load the white pawns
            self.pieces[i] = Pawn(i, WHITE)
        for i in range(48, 56):
            # load the black pawns
            self.pieces[i] = Pawn(i, PIECEBLACK)
        for i in range(8):
            # Load the special pieces for the front row and color them white
            self.pieces[i] = pieceOrder[i](i, WHITE)
            # Load the special pieces for the back row and color them black
            self.pieces[i + 56] = pieceOrder[i](i + 56, PIECEBLACK)

        # This will represent the index of the currently highlited square
        self.hiSq = False
        # This wil represent the index of the square where currently dragged piece
        # was grabbed from
        self.dragging = False

        # Start the task that handles the picking
        self.mouseTask = taskMgr.add(self.mouseTask, 'mouseTask')
        self.accept("mouse1", self.grabPiece)  # left-click grabs a piece
        self.accept("mouse1-up", self.releasePiece)  # releasing places it

    # This function swaps the positions of two pieces
    def swapPieces(self, fr, to):
        temp = self.pieces[fr]
        self.pieces[fr] = self.pieces[to]
        self.pieces[to] = temp
        if self.pieces[fr]:
            self.pieces[fr].square = fr
            self.pieces[fr].obj.setPos(SquarePos(fr))
        if self.pieces[to]:
            self.pieces[to].square = to
            self.pieces[to].obj.setPos(SquarePos(to))

    def trashPiece(self, index):
        self.pieces[index].obj.setPos(trash())
        self.pieces[index] = None

    def mouseTask(self, task):

        if self.hiSq is not False:
            self.squares[self.hiSq].setColor(SquareColor(self.hiSq))
            self.hiSq = False

        if self.mouseWatcherNode.hasMouse():
            # get the mouse position
            mpos = self.mouseWatcherNode.getMouse()

            # Set the position of the ray based on the mouse position
            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

            # If we are dragging something, set the position of the object
            # to be at the appropriate point over the plane of the board
            if self.dragging is not False:
                # Gets the point described by pickerRay.getOrigin(), which is relative to
                # camera, relative instead to render
                nearPoint = render.getRelativePoint(
                    camera, self.pickerRay.getOrigin())
                # Same thing with the direction of the ray
                nearVec = render.getRelativeVector(
                    camera, self.pickerRay.getDirection())
                self.pieces[self.dragging].obj.setPos(
                    PointAtZ(.5, nearPoint, nearVec))

            self.picker.traverse(self.squareRoot)
            if self.pq.getNumEntries() > 0:
                self.pq.sortEntries()
                i = int(self.pq.getEntry(0).getIntoNode().getTag('square'))
                # Set the highlight on the picked square
                
                if (self.dragging != False or (isinstance(self.pieces[i], Piece) and self.pieces[i].obj.getColor() == self.turn)):
                    if (isinstance(self.movingPiece, Piece)):
                        if (isinstance(self.pieces[i], Piece) and self.pieces[i].obj.getColor() != self.turn):
                            movementTable = self.movingPiece.getMovementTableBattle()
                        else:
                            movementTable = self.movingPiece.getMovmentTableNoBattle()
                        if (self.checkIfRoutePossible(self.movingPieceIndex, i, movementTable)):
                            self.squares[i].setColor(HIGHLIGHT_POSITIVE)
                            self.isMovementPossible = True
                        else:
                            self.squares[i].setColor(HIGHLIGHT_NEGATIVE)
                            self.isMovementPossible = False
                    self.hiSq = i

        return Task.cont

    def grabPiece(self):
        if self.hiSq is not False and self.pieces[self.hiSq]:
            self.movingPiece = self.pieces[self.hiSq]
            self.movingPieceIndex = self.hiSq
            self.dragging = self.hiSq
            self.hiSq = False

    def releasePiece(self):
        if self.dragging is not False:
            if self.hiSq is False or not self.isMovementPossible or (isinstance(self.pieces[self.dragging], Piece) and isinstance(self.pieces[self.hiSq], Piece) and self.pieces[self.dragging].obj.getColor() == self.pieces[self.hiSq].obj.getColor()):
                self.pieces[self.dragging].obj.setPos(
                    SquarePos(self.dragging))
            else:
                # Otherwise, swap the pieces
                self.swapPieces(self.dragging, self.hiSq)
                if (isinstance(self.pieces[self.dragging], Piece) and self.dragging != self.hiSq and self.pieces[self.dragging].obj.getColor() != self.pieces[self.hiSq].obj.getColor()):
                    self.trashPiece(self.dragging)
                    print('trashed')
                
                if (not isinstance(self.movingPiece, type(None)) and self.movingPiece.isPawn() and self.dragging != self.hiSq):
                    self.movingPiece.setFirstMove(False)
                self.isCheck(self.hiSq)
                self.changeTurn()

        self.dragging = False
        self.movingPiece = None
        self.movingPieceIndex = -1

    def setupLights(self):  # This function sets up some default lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.8, .8, .8, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(LVector3(0, 45, -45))
        directionalLight.setColor((0.2, 0.2, 0.2, 1))
        render.setLight(render.attachNewNode(directionalLight))
        render.setLight(render.attachNewNode(ambientLight))

    def changeTurn(self):
        if self.turn == WHITE:
            self.turn = PIECEBLACK
        else:
            self.turn = WHITE

    def isCheck(self, index):
        kingIndex = 0
        for i in range(0, 64):
            if (isinstance(self.pieces[i], King) and self.pieces[i].obj.getColor() != self.turn):
                kingIndex = i
        for j in range(0, 64):
            if (isinstance(self.pieces[index], Piece) and self.pieces[index].obj.getColor() == self.turn):
                if(self.checkIfRoutePossible(index, kingIndex, self.pieces[index].getMovementTableBattle())):
                    global check
                    print("CHECK FOUND")
                    label = "white"
                    if self.turn == WHITE:
                        label = "black"
                    check = OnscreenText(
                    text="Check on " + label + " king",
                    parent=base.a2dTopLeft, align=TextNode.ALeft,
                    style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.26), scale=.05)
                elif (not isinstance(check, type(None))):
                    print("Should remove now")
                    check.destroy()
                    check = None
                    


class Piece(object):
    def __init__(self, square, color):
        self.obj = loader.loadModel(self.model)
        self.obj.reparentTo(render)
        self.obj.setColor(color)
        self.obj.setPos(SquarePos(square))

    def getMovmentTableNoBattle(self):
        pass

    def getMovementTableBattle(self):
        pass

    def isPawn(self):
        return False


class Pawn(Piece):
    model = "models/pawn"

    def __init__(self, square, color):
        Piece.__init__(self, square, color)
        self.firstMove = True

    def setFirstMove(self, isFirstMove):
        self.firstMove = isFirstMove

    def getMovmentTableNoBattle(self):
        if self.firstMove:
            return [[0, 2, 0], [0, 0, 0], [0, 0, 0]]
        else:
            return [[0, 1, 0], [0, 0, 0], [0, 0, 0]]

    def getMovementTableBattle(self):
        return [[1, 0, 1], [0, 0, 0], [0, 0, 0]]

    def isPawn(self):
        return True

class King(Piece):
    model = "models/king"
    def getMovmentTableNoBattle(self):
            return [[1, 1, 1], [1, 0, 1], [1, 1, 1]]

    def getMovementTableBattle(self):
        return [[1, 1, 1], [1, 0, 1], [1, 1, 1]]

class Queen(Piece):
    model = "models/queen"
    def getMovmentTableNoBattle(self):
            return [[8, 8, 8], [8, 8, 8], [8, 8, 8]]

    def getMovementTableBattle(self):
        return [[8, 8, 8], [8, 8, 8], [8, 8, 8]]

class Bishop(Piece):
    model = "models/bishop"
    def getMovmentTableNoBattle(self):
            return [[8, 0, 8], [0, 0, 0], [8, 0, 8]]

    def getMovementTableBattle(self):
        return [[8, 0, 8], [0, 0, 0], [8, 0, 8]]

class Knight(Piece):
    def getMovmentTableNoBattle(self):
            return [6, 15, 17, 10, -10, -17, -15, -6]

    def getMovementTableBattle(self):
        return [6, 15, 17, 10, -10, -17, -15, -6]
    model = "models/knight"

class Rook(Piece):
    model = "models/rook"
    def getMovmentTableNoBattle(self):
            return [[0, 8, 0], [8, 0, 8], [0, 8, 0]]

    def getMovementTableBattle(self):
        return [[0, 8, 0], [8, 0, 8], [0, 8, 0]]

demo = ChessboardDemo()
demo.run()
