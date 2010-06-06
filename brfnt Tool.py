#!/usr/bin/env python

# This is only needed for Python v2 but is harmless for Python v3.
import sip, struct, sys, os, TPL
#sip.setapi('QVariant', 2)

from PyQt4 import QtCore, QtGui

Encoding = None

def module_path():
    """This will get us the program's directory, even if we are frozen using py2exe"""
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    if __name__ == '__main__':
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    return None


def GetIcon(name):
    """Helper function to grab a specific icon"""
    return QtGui.QIcon('data/icon_%s.png' % name)


class Window(QtGui.QMainWindow):
    """Main Window"""
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self, None)
        self.savename = ''

        self.CreateFileMenu()
        
        centralWidget = QtGui.QWidget()

        self.view = ViewWidget()

        self.brfntScene = QtGui.QGraphicsScene()
        self.systemWidget = QtGui.QGraphicsScene()

        self.leading = QtGui.QCheckBox("Leading")
        self.ascent = QtGui.QCheckBox("Ascent")
        self.baseline = QtGui.QCheckBox("Baseline")

        self.view.characterSelected.connect(self.expandedData)
        self.leading.stateChanged.connect(self.view.updateLeading)
        self.ascent.stateChanged.connect(self.view.updateAscent)
        self.baseline.stateChanged.connect(self.view.updateBaseline)

        centralLayout = QtGui.QVBoxLayout()
        topLayout = QtGui.QHBoxLayout()
        topLayout.addWidget(self.leading)
        topLayout.addWidget(self.ascent)
        topLayout.addWidget(self.baseline)
        centralLayout.addLayout(topLayout)
        centralLayout.addWidget(self.view)
        centralWidget.setLayout(centralLayout)

        self.setCentralWidget(centralWidget)
        self.setWindowTitle('Brfnt-ify')
        self.setWindowIcon(QtGui.QIcon('data/icon.png'))
        self.resize(600, 800)        

        self.previewWindow = PreviewWindow(self)
        self.previewWindow.setWindowFlags(self.previewWindow.windowFlags() | QtCore.Qt.Drawer)



    def expandedData(self, character):
        return
        
        
    def HandleImport(self):
        """Import an image"""
         
        # File Dialog        
        fn = QtGui.QFileDialog.getOpenFileName(self, 'Choose a script file', '', 'Plain Text File (*.txt);;All Files(*)')
        if fn == '': return
        fn = str(fn)
        
        
    def HandleGenerate(self):
        """Generate a font"""
        
        dlg = GenerateDialog()
        if dlg.exec_() == QtGui.QDialog.Accepted:
            # Create ta bunch of glyphs, I guess.

            charrange = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
            
            global Encoding
            Encoding = 'UTF-8'
            FontItems = []

#            print fontMetrics.maxWidth()
#            print fontMetrics.height()
#            print fontMetrics.ascent()
#            print fontMetrics.descent()
#            print fontMetrics.averageCharWidth()
#            print fontMetrics.leading()
#            print fontMetrics.lineSpacing()
#            print fontMetrics.lineWidth()
#            print fontMetrics.minLeftBearing()
#            print fontMetrics.minRightBearing()
#            print fontMetrics.overlinePos()
#            print fontMetrics.xHeight()
                
                
            newFont = dlg.fontCombo.currentFont()
            newFont.setPointSize(int(dlg.sizeCombo.currentText()))
            if dlg.styleCombo.currentIndex() == 1:
                newFont.setBold(True)
            elif dlg.styleCombo.currentIndex() == 2:
                newFont.setStyle(1)
            elif dlg.styleCombo.currentIndex() == 3:            
                newFont.setStyle(1)
                newFont.setBold(True)

            fontMetrics = QtGui.QFontMetrics(newFont)

            for glyph in charrange:
                # make a pixmap
                tex = QtGui.QImage(fontMetrics.averageCharWidth()*1.5, fontMetrics.height(), QtGui.QImage.Format_RGB32)
                tex.fill(QtCore.Qt.black)
                painter = QtGui.QPainter(tex)
                painter.setPen(QtCore.Qt.white)
                painter.setFont(newFont)
                painter.drawText(0-fontMetrics.leftBearing(QtCore.QChar(glyph)), fontMetrics.ascent(), QtCore.QChar(glyph))
                                
                painter.end()
                
                newtex = QtGui.QPixmap.fromImage(tex)
                # append a glyph to FontItems
                FontItems.append(Glyph(newtex, ord(glyph), 0, 0, 0))
               
            
            self.rfnt = brfntHeader(0xFFFE, 0x0104, 0)
            self.finf = FontInformation(1, fontMetrics.leading(), '', fontMetrics.minLeftBearing(), fontMetrics.maxWidth(), fontMetrics.maxWidth(), 'UTF-8', fontMetrics.height(), fontMetrics.maxWidth(), fontMetrics.ascent(), fontMetrics.descent())
            self.tglp = TextureInformation(fontMetrics.maxWidth(), fontMetrics.height(), fontMetrics.ascent() + 1, fontMetrics.maxWidth(), 0, 5, 1, 5, 5, 0, 0)
               
            x = 0
            y = 0
            i = 0
            self.systemWidget.clear()
            self.systemWidget.setSceneRect(0, 0, 5000, 5000)

            for item in FontItems:
                if i >= 30:
                    x = 0
                    y = y + item.pixmap.height()
                    i = 0
                item.setPos(x, y)
                self.systemWidget.addItem(item)
                x = x + item.pixmap.width()
                i += 1
                            
            self.view.updateDisplay(self.rfnt, self.finf, self.tglp)
            self.view.setScene(self.systemWidget)    


    def HandleOpen(self):
        """Open a Binary Revolution Font (.brfnt) file for Editing"""

        # File Dialog        
        fn = QtGui.QFileDialog.getOpenFileName(self, 'Choose a Font', '', 'Binary Revolution Font (*.brfnt)')
        if fn == '': return
        fn = str(fn)
        i = 0

        with open(fn) as f:
            tmpf = f.read()
        f.close()
        
        RFNT = struct.unpack_from('>IHHIHH', tmpf[0:16])
        FINF = struct.unpack_from('>IIBbHbBbBIIIBBBB', tmpf[16:48])
        TGLP = struct.unpack_from('>IIBBbBIHHHHHHI', tmpf[48:96])
        CWDH = struct.unpack_from('>3Ixxxx', tmpf, FINF[10] - 8)
        CWDH2 = []
        CMAP = []
        
        
        position = FINF[10] + 8
        for i in xrange(CWDH[2]+1):
            Entry = struct.unpack_from('>bBb', tmpf, position)
            position += 3
            CWDH2.append((Entry[0], Entry[1], Entry[2]))
        
        position = FINF[11]
        while position != 0:
            Entry = struct.unpack_from('>HHHxxIH', tmpf, position) # 0: start range -- 1: end range -- 2: type -- 3: position -- 4: CharCode List
            if Entry[2] == 0:
                index = Entry[4]
                for glyph in range(Entry[0], Entry[1]+1):
                    CMAP.append((index, glyph))
                    index += 1
            
            elif Entry[2] == 1:
                indexdat = tmpf[(position+12):(position+12+((Entry[1]-Entry[0]+1)*2))]
                entries = struct.unpack(">" + str(len(indexdat)/2) + "H", indexdat)
                i = 0
                for glyph in range(Entry[0], Entry[1]+1):
                    index = entries[i]
                    if index == 0xFFFF:
                        pass
                    else:
                        CMAP.append((index, glyph))
                        
                    i += 1
            
            elif Entry[2] == 2:
                entries = struct.unpack_from('>' + str(Entry[4]*2) + 'H', tmpf, position+0xE)
                i = 0
                for p in xrange(Entry[4]):
                    CMAP.append((entries[i+1],entries[i]))
                    i += 2
                            
            else:
                print "Unknown CMAP type!"
                break
            
            position = Entry[3]
        
        
        self.rfnt = brfntHeader(RFNT[1], RFNT[2], RFNT[5])
        self.finf = FontInformation(FINF[2], FINF[3], FINF[4], FINF[5], FINF[6], FINF[7], FINF[8], FINF[12], FINF[13], FINF[14], FINF[15])
        self.tglp = TextureInformation(TGLP[2], TGLP[3], TGLP[4], TGLP[5], TGLP[6], TGLP[7], TGLP[8], TGLP[9], TGLP[10], TGLP[11], TGLP[12])
        
        global Encoding
        if self.finf.encoding == 1:
            Encoding = "UTF-16BE"
        elif self.finf.encoding == 2:
            Encoding = "SJIS"
        elif self.finf.encoding == 3:
            Encoding = "windows-1252"
        elif self.finf.encoding == 4:
            Encoding = "hex"
        else:
            Encoding = "UTF-8"
        
        
        TPLDat = tmpf[96:(TGLP[1] + 48)]
        w = self.tglp.width
        h = self.tglp.height


        self.previewWindow.updateFields(self)

        SingleTex = []
        Images = []
        length = self.tglp.textureSize
        offset = 0
        charsPerTex = self.tglp.column * self.tglp.row
        
        for tex in xrange(self.tglp.amount):
            SingleTex.append(struct.unpack(">" + str(length) + "B", TPLDat[offset:length+offset]))
            offset += length

        for tex in SingleTex:
            dest = QtGui.QImage(w,h,QtGui.QImage.Format_ARGB32)
            dest.fill(QtCore.Qt.black)

            dest = TPL.Decode(dest, tex, w, h, self.tglp.type)
            
            y = 0
            for a in xrange(self.tglp.row):
                x = 0
                for b in xrange(self.tglp.column):
                    Images.append(QtGui.QPixmap.fromImage(dest.copy(x, y, self.tglp.cellWidth, self.tglp.cellHeight)))
                    x += self.tglp.cellWidth
                y += self.tglp.cellHeight
                

        self.brfntScene.clear()
        self.brfntScene.setSceneRect(0, 0, self.tglp.cellWidth * 30, self.tglp.cellHeight * (((self.tglp.row * self.tglp.column * self.tglp.amount) / 30) + 1))
                        
        


        CMAP.sort(key=lambda x: x[0])

        for i in range(len(CMAP), len(Images)):
            CMAP.append((0xFFFF,0xFFFF))

        for i in range(len(CWDH2), len(Images)):
            CWDH2.append((0xFF,0xFF,0xFF))
            

        FontItems = []
        i = 0
        for tex in Images:
            FontItems.append(Glyph(tex, CMAP[i][1], CWDH2[i][0], CWDH2[i][1], CWDH2[i][2]))
            i += 1
        x = 0
        y = 0
        i = 0
        for item in FontItems:
            if i >= 30:
                x = 0
                y = y + item.pixmap.height()
                i = 0
            item.setPos(x, y)
            self.brfntScene.addItem(item)
            x = x + item.pixmap.width()
            i += 1

        self.view.updateDisplay(self.rfnt, self.finf, self.tglp)
        self.view.setScene(self.brfntScene)    
            
        window.savename = fn
    

    def HandleSave(self):
        """Save a level back to the archive"""
        if not window.savename:
            window.HandleSaveAs()
            return
        
        window.Saving(window.savename)
   
        
    def HandleSaveAs(self):
        """Pack up the level files using the translations if available"""
        fn = QtGui.QFileDialog.getSaveFileName(self, 'Choose a new filename', '', 'Binary Revolution Font (*.brfnt);;All Files(*)')
        if fn == '': return
        fn = str(fn)
        window.Saving(fn)
        
        window.savename = fn


    def Saving(parent, fn):

        print 'creating font file'


    def CreateFileMenu(self):
        """Helper function to create the menus"""
        # create the actions
        self.actions = {}
        self.CreateAction('open', self.HandleOpen, GetIcon('open'), 'Open...', 'Open a script file', QtGui.QKeySequence.Open)
        self.CreateAction('save', self.HandleSave, GetIcon('save'), 'Save', 'Save a script file', QtGui.QKeySequence.Save)
        self.CreateAction('saveas', self.HandleSaveAs, GetIcon('saveas'), 'Save as...', 'Save a copy of the script file', QtGui.QKeySequence.SaveAs)
        self.CreateAction('generate', self.HandleGenerate, None, 'Generate', 'Generate a font table from an installed font', QtGui.QKeySequence('Ctrl+G'))
        self.CreateAction('import', self.HandleImport, None, 'Import', 'Import a txt to the current displayed script', QtGui.QKeySequence('Ctrl+I'))

        # create a menubar        
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.actions['open'])
        self.fileMenu.addAction(self.actions['save'])
        self.fileMenu.addAction(self.actions['saveas'])
        self.fileMenu.addAction(self.actions['generate'])
        self.fileMenu.addAction(self.actions['import'])
        self.menuBar().addMenu(self.fileMenu)

     
    def CreateAction(self, shortname, function, icon, text, statustext, shortcut, toggle=False):
        """Helper function to create an action"""
        
        if icon != None:
            act = QtGui.QAction(icon, text, self)
        else:
            act = QtGui.QAction(text, self)
        
        if shortcut != None: act.setShortcut(shortcut)
        if statustext != None: act.setStatusTip(statustext)
        if toggle:
            act.setCheckable(True)
        act.triggered.connect(function)
        
        self.actions[shortname] = act



class GenerateDialog(QtGui.QDialog):
    """Allows the user to generate a glyph table from an installed font                                                                                                                                                                                                                                       """
    def __init__(self):
        """Creates and initialises the dialog"""
        QtGui.QDialog.__init__(self)
        self.setWindowTitle('Generate a Font')
        
        # Font Setting Groups
        self.fontGroupBox = QtGui.QGroupBox("Font Generation")

        self.fontCombo = QtGui.QFontComboBox()
        self.sizeCombo = QtGui.QComboBox()
        self.styleCombo = QtGui.QComboBox()
        self.charrange = QtGui.QLineEdit()

        fontlayout = QtGui.QGridLayout()
        fontlayout.addWidget(QtGui.QLabel("Font:"), 0, 0, 1, 1, QtCore.Qt.AlignRight)
        fontlayout.addWidget(self.fontCombo, 0, 1, 1, 3)
        fontlayout.addWidget(QtGui.QLabel("Size:"), 1, 0, 1, 1, QtCore.Qt.AlignRight)
        fontlayout.addWidget(self.sizeCombo, 1, 1, 1, 1)
        fontlayout.addWidget(QtGui.QLabel("Style:"), 1, 2, 1, 1, QtCore.Qt.AlignRight)
        fontlayout.addWidget(self.styleCombo, 1, 3, 1, 1)
        fontlayout.addWidget(QtGui.QLabel("Character Range:"), 2, 0, 1, 1, QtCore.Qt.AlignRight)
        fontlayout.addWidget(self.charrange, 2, 1, 1, 3)
        self.fontGroupBox.setLayout(fontlayout)

        self.styleCombo.addItems(['Normal', 'Bold', 'Italic', 'Bold Italic'])
        self.findSizes(self.fontCombo.currentFont())

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        Layout = QtGui.QVBoxLayout()
        Layout.addWidget(self.fontGroupBox)
        Layout.addWidget(buttonBox)    

        self.setLayout(Layout)


    def findSizes(self, font):
        fontDatabase = QtGui.QFontDatabase()
        currentSize = self.sizeCombo.currentText()
        self.sizeCombo.blockSignals(True)
        self.sizeCombo.clear()

        if fontDatabase.isSmoothlyScalable(font.family(), fontDatabase.styleString(font)):
            for size in QtGui.QFontDatabase.standardSizes():
                self.sizeCombo.addItem(str(size))
                self.sizeCombo.setEditable(True)
        else:
            for size in fontDatabase.smoothSizes(font.family(), fontDatabase.styleString(font)):
                self.sizeCombo.addItem(str(size))
                self.sizeCombo.setEditable(False)

        self.sizeCombo.blockSignals(False)

        sizeIndex = self.sizeCombo.findText(currentSize)
        if sizeIndex == -1:
            self.sizeCombo.setCurrentIndex(max(0, self.sizeCombo.count() / 3))
        else:
            self.sizeCombo.setCurrentIndex(sizeIndex)


class Glyph(QtGui.QGraphicsItem):
    """Class for a character glyph"""
    
    def __init__(self, pixmap, glyph = None, leftmargin = 0, charwidth = 0, fullwidth = 0):
        """Generic constructor for glyphs"""
        QtGui.QGraphicsPixmapItem.__init__(self)
        
        self.glyph = glyph
        self.leftmargin = leftmargin
        self.charwidth = charwidth
        self.fullwidth = fullwidth
        self.pixmap = pixmap
        self.boundingRect = QtCore.QRectF(0,0,pixmap.width(),pixmap.height())
        self.selectionRect = QtCore.QRectF(0,0,pixmap.width()-1,pixmap.height()-1)

        buffer = struct.pack(">H", self.glyph)
        self.EncodeChar = (struct.unpack(">2s", buffer))[0].decode(Encoding, "replace")
        
        if self.glyph != None:
            text = QtCore.QString.fromLatin1("<p>Character: <span style=\"font-size: 24pt;\">") + \
                    QtCore.QString(self.EncodeChar) + \
                    QtCore.QString.fromLatin1("</span><p>Value: 0x") + \
                    QtCore.QString.number(self.glyph, 16)
        else:
            text = QtCore.QString.fromLatin1("<p>Character: <span style=\"font-size: 24pt;\">Unknown Glyph")
        
        
        self.setToolTip(text)
        self.setFlag(self.ItemIsMovable, False)
        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemIsFocusable, True)
        

    def setGlyph(self, glyph):
        self.glyph = glyph
        
    def setWidths(self, a, b, c):
        self.leftmargin = a
        self.charwidth = b
        self.fullwidth = c
        
    def boundingRect(self):
        """Required for Qt"""
        return self.boundingRect

    def setPixmap(self, pict):
        self.pixmap = pict
        
        
    def paint(self, painter, option, widget):
        """Paints the object"""

        painter.drawPixmap(0, 0, self.pixmap)

        if self.isSelected():
            painter.setPen(QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.SolidLine))
            painter.drawRect(self.selectionRect)
            painter.fillRect(self.selectionRect, QtGui.QColor.fromRgb(255,255,255,64))
            print dir(self)
            
            print dir(self.parentWidget)
            print dir(parent)
            self.previewwindow.updateCWDH(self.EncodeChar, self.leftmargin, self.charwidth, self.fullwidth)
        

class PreviewWindow(QtGui.QWidget):
    def __init__(self, parent):
        super(PreviewWindow, self).__init__(parent)


        # Metrics Group

        self.defaultchar = QtGui.QLineEdit() # Default char for exceptions
        self.defaultchar.setMaxLength(1) 
        self.defaultchar.setMaximumWidth(30)

        self.fonttype = 0
        self.leading = 0
        self.leftmargin = 0
        self.charwidth = 0
        self.fullwidth = 0
        self.encoding = "None"
        self.height = 0
        self.width = 0
        self.ascent = 0
        self.baseLine = 0
        self.format = "None"
        self.controlsLayout = QtGui.QVBoxLayout()

        self.setupGui()

        self.setLayout(self.controlsLayout)

        self.setWindowTitle("Metrics")
        
    
    def setupGui(self):

        
        # Font
        font = QtGui.QFont()
        font.setPointSize(10)

        metricsGroupBox = QtGui.QGroupBox("Font Metrics")


        self.labeltext = ["Font Type:", self.fonttype, "Leading:", self.leading, "Default Char:", "Left Bearing:", self.leftmargin, "Char Width:", self.charwidth, "Full Width:", self.fullwidth, "Encoding:", self.encoding, "Height:", self.height, "Width:", self.width, "Ascent:", self.ascent, "Baseline:", self.baseLine, "Texture Format:", self.format]
        self.label = []
        for i in xrange(len(self.labeltext)):
            
            self.label.append(QtGui.QLabel(str(self.labeltext[i])))
            self.label[i].setFont(font)
        

        self.glyphBox = QtGui.QLabel("0")
        self.cwdh1 = QtGui.QLabel("0")
        self.cwdh2 = QtGui.QLabel("0")
        self.cwdh3 = QtGui.QLabel("0")

        Leadings = QtGui.QFormLayout()
        Leadings.addRow(self.label[2], self.label[3])
        Leadings.addRow(self.label[17], self.label[18])
        Leadings.addRow(self.label[19], self.label[20])

        Widths = QtGui.QFormLayout()
        Widths.addRow(self.label[5], self.label[6])
        Widths.addRow(self.label[7], self.label[8])
        Widths.addRow(self.label[9], self.label[10])

        Font = QtGui.QFormLayout()
        Font.addRow(self.label[0], self.label[1])
        Font.addRow(self.label[11], self.label[12])
        Font.addRow(self.label[21], self.label[22])
        Font.addRow(self.label[4], self.defaultchar)

        Character = QtGui.QFormLayout()
        Character.addRow(QtGui.QLabel("Glyph:"), self.glyphBox)
        Character.addRow(QtGui.QLabel("Left Margin:"), self.cwdh1)
        Character.addRow(QtGui.QLabel("Char Width:"), self.cwdh2)
        Character.addRow(QtGui.QLabel("Full Width:"), self.cwdh3)

        metricslayout = QtGui.QVBoxLayout()
        metricslayout.addLayout(Font)
        metricslayout.addLayout(Widths)
        metricslayout.addLayout(Leadings)
        metricslayout.addLayout(Character)
        metricsGroupBox.setLayout(metricslayout)


        closeButton = QtGui.QPushButton("&Hide")
        closeButton.clicked.connect(self.close)

        self.controlsLayout.addWidget(metricsGroupBox)
        self.controlsLayout.addWidget(closeButton)    

    
    def updateFields(self, parent):
        
        self.label[1].setText(str(parent.finf.fonttype))
        self.label[3].setText(str(parent.finf.leading))
        self.defaultchar.setText(QtCore.QChar(parent.finf.defaultchar))
        self.label[6].setText(str(parent.finf.leftmargin))
        self.label[8].setText(str(parent.finf.charwidth))
        self.label[10].setText(str(parent.finf.fullwidth))
        self.label[12].setText(Encoding)
        self.label[20].setText(str(parent.finf.ascent))
        self.label[18].setText(str(parent.tglp.baseLine))
        
        formatlist = ["I4", "I8", "IA4", "IA8", "RGB4A3", "RGB565", "RGBA8", "-----------", "CI4", "CI8", "CI14x2", "-----------", "-----------", "-----------", "CMPR/S3TC"]
        self.label[22].setText(formatlist[parent.tglp.type])
        
        
    def updateCDWH(self, glyph, cwdh1, cwdh2, cwdh3):
    
        self.glyphBox.setText(glyph)
        self.cwdh1.setText(cwdh1)
        self.cwdh2.setText(cwdh2)
        self.cwdh3.setText(cwdh3)
        
        
class ViewWidget(QtGui.QGraphicsView):

    characterSelected = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(ViewWidget, self).__init__(parent)

        self.Images = []
        self.drawLeading = False
        self.drawAscent = False
        self.drawBaseline = False

        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor.fromRgb(119,136,153)))
        self.setMouseTracking(True)
        self.YScrollBar = QtGui.QScrollBar(QtCore.Qt.Vertical, parent)
        self.XScrollBar = QtGui.QScrollBar(QtCore.Qt.Horizontal, parent)



    def updateDisplay(self, rfnt, finf, tglp):            
        self.rfnt = rfnt
        self.finf = finf
        self.tglp = tglp
        self.update()

    def updateLeading(self, checked):
        if checked:
            self.drawLeading = True
        else:
            self.drawLeading = False
        self.update()

    def updateAscent(self, checked):
        if checked:
            self.drawAscent = True
        else:
            self.drawAscent = False
        self.update()

    def updateBaseline(self, checked):
        if checked:
            self.drawBaseline = True
        else:
            self.drawBaseline = False
        self.update()


    def sizeHint(self):
        return QtCore.QSize(5000, 5000)

    def drawForeground(self, painter, rect):
        rows = (((self.tglp.row * self.tglp.column * self.tglp.amount) / 30) + 2)
    
        
        
        drawLine = painter.drawLine
        painter.setPen(QtGui.QPen(QtGui.QColor.fromRgb(255,0,0,255), 2))
    
        if self.drawLeading:
            for i in xrange(rows):
                drawLine(0, ((i-1)* self.tglp.cellHeight) + self.finf.leading, self.tglp.cellWidth * 30, ((i-1)* self.tglp.cellHeight) + self.finf.leading)


        painter.setPen(QtGui.QPen(QtGui.QColor.fromRgb(0,255,0,255), 2))

        if self.drawAscent:
            for i in xrange(rows):
                drawLine(0, ((i)* self.tglp.cellHeight) - self.finf.ascent, self.tglp.cellWidth * 30, ((i)* self.tglp.cellHeight) - self.finf.ascent)


        painter.setPen(QtGui.QPen(QtGui.QColor.fromRgb(0,0,255,255), 2))
        
        if self.drawBaseline:
            for i in xrange(rows):
                drawLine(0, ((i-1)* self.tglp.cellHeight) + self.tglp.baseLine, self.tglp.cellWidth * 30, ((i-1)* self.tglp.cellHeight) + self.tglp.baseLine)
        
        


class brfntHeader():
    """Represents the brfnt header"""
    
    def __init__(self, vmajor, vminor, chunkcount):
        """Constructor"""
 
        self.versionmajor = vmajor      # Major Font Version (0xFFFE)
        self.versionminor = vminor      # Minor Font Version (0x0104)
        self.chunkcount = chunkcount    # Number of chunks in the file
        
        
class FontInformation():
    """Represents the finf section"""
    
    def __init__(self, fonttype, leading, defaultchar, leftmargin, charwidth, fullwidth, encoding, height, width, ascent, descent):
        """Constructor"""

        self.fonttype = fonttype                #
        self.leading = leading +1               # http://en.wikipedia.org/wiki/Leading
        self.defaultchar = defaultchar          # Default char for exceptions
        self.leftmargin = leftmargin            # 
        self.charwidth = charwidth +1           # 
        self.fullwidth = fullwidth +1           # 
        self.encoding = encoding                # In order - UTF-8, UTF-16, SJIS, CP1252, COUNT
        self.height = height +1                 # 
        self.width = width +1                   # 
        self.ascent = ascent                    # 
        self.descent = descent                  # 
        
        
class TextureInformation():
    """Represents the Texture Pallete Group header"""
    
    def __init__(self, cellWidth, cellHeight, baseLine, maxCharWidth, texsize, texNum, texType, column, row, width, height):
        """Constructor"""
        self.cellWidth = cellWidth + 1          # Font Width (0 base)
        self.cellHeight = cellHeight + 1        # Font Height (0 base)
        self.baseLine = baseLine + 1            # Position of baseline from top (0 base)
        self.maxCharWidth = maxCharWidth + 1    # Maximum width of a single character (0 base)
        self.textureSize = texsize              # Length of texture in bytes
        self.amount = texNum                    # Number of textures in the TGLP
        self.type = texType                     # TPL format
        self.column = column                    # Number of characters per column
        self.row = row                          # Number of characters per row
        self.width = width                      # Width of a texture
        self.height = height                    # Height of a texture



if __name__ == '__main__':

    path = module_path()
    if path != None:
        os.chdir(module_path())


    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
