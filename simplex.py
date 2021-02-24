import sys
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QStyledItemDelegate, QVBoxLayout, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel, QGridLayout, QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem, QItemDelegate
from PyQt5.QtGui import QIcon, QRegExpValidator, QTextTable
from PyQt5.QtCore import QRegExp, pyqtSlot, Qt

#Clase delegate para campos que no deben ser modificados
class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return

#Clase delegate para campos que solo admiten numeros
class NumberOnlyDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        dSpinBox = QtWidgets.QDoubleSpinBox(parent)
        dSpinBox.setDecimals(4)
        dSpinBox.setMaximum(9999.9999)
        if index.column() > 1:
            return dSpinBox             

class App(QWidget):
    colPivot = 0
    filaPivot = 0

    def __init__(self):
        super().__init__()
        self.title = 'Programa Simplex'
        self.left = 50
        self.top = 50
        self.width = 1080
        self.height = 480
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createGridLayout()

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        self.show()
    
    def createGridLayout(self):
        self.horizontalGroupBox = QGroupBox()
        layout = QGridLayout()

        #Expresion regular para las cajas de texto
        rx = QRegExp("\d+")

        #Cajas de texto
        label = QLabel('Cantidad de productos')
        textbox = QLineEdit()
        textbox.setMaximumWidth(100)
        textbox.setMaxLength(2)
        textbox.setValidator(QRegExpValidator(rx))
        label1 = QLabel('Cantidad de restricciones')
        textbox1 = QLineEdit()
        textbox1.setMaximumWidth(100)
        textbox1.setMaxLength(2)
        textbox1.setValidator(QRegExpValidator(rx))
        
        #Boton para procesar los datos ingresados
        buttonOk = QPushButton('Generar Tablas')
        buttonOk.setToolTip('Generar Tablas')
        buttonOk.setMaximumWidth(100)

        #Tabla para llenar datos iniciales
        table = QTableWidget()
        table.setMinimumHeight(210)
        table.setMaximumWidth(500)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        
        #Tabla para muestra de resultados
        tableRes = QTableWidget()
        tableRes.setMaximumWidth(800)
        tableRes.setMinimumHeight(300)
        tableRes.verticalHeader().setVisible(False)
        tableRes.horizontalHeader().setVisible(False)

        #Crea la tabla para llenar los datos iniciales
        buttonOk.clicked.connect(lambda: self.createTables(self, table, tableRes, textbox.text(), 
                                                            textbox1.text(), textbox, textbox1, buttonOk, buttonCalcular))
        self.buttonGroup = QGroupBox()

        #Grid para los botones
        buttonLayout = QGridLayout()
        buttonLayout.setRowStretch(2,0)
        
        #Botones de accion
        buttonCalcular = QPushButton('Calcular')
        buttonCalcular.setToolTip('Calcular')
        buttonCalcular.setMaximumWidth(100)
        buttonCalcular.setDisabled(True)
        buttonSiguiente = QPushButton('Siguiente')
        buttonSiguiente.setToolTip('Siguiente calculo')
        buttonSiguiente.setMaximumWidth(100)
        buttonSiguiente.setDisabled(True)
        buttonNuevo = QPushButton('Nuevo')
        buttonNuevo.setToolTip('Ingresar datos nuevamente')
        buttonNuevo.setMaximumWidth(100)
        buttonNuevo.setDisabled(True)

        self.buttonGroup.setLayout(buttonLayout)

        buttonLayout.addWidget(buttonCalcular,0,0,Qt.AlignCenter)
        buttonLayout.addWidget(buttonSiguiente,1,0,Qt.AlignCenter)
        buttonLayout.addWidget(buttonNuevo,2,0,Qt.AlignCenter)

        #Accion para el boton calcular
        buttonCalcular.clicked.connect(lambda: self.calcular(self, table, tableRes, textbox.text(), textbox1.text()
                                        , buttonCalcular, buttonSiguiente))

        #Accion para el boton siguiente
        buttonSiguiente.clicked.connect(lambda: self.calcularSiguiente(self, tableRes, textbox.text(), textbox1.text(),
                                        buttonSiguiente, buttonNuevo))

        #Accion para el boton nuevo
        buttonNuevo.clicked.connect(lambda: self.nuevoCalculo(textbox, textbox1, buttonOk, buttonNuevo, table, tableRes))
 
        layout.setRowStretch(0,4)
        layout.setRowStretch(1,2)
        layout.setRowStretch(2,4)
        layout.setColumnStretch(1,0)
    
        #Se generan los widgets en el grid
        layout.addWidget(label,0,0,Qt.AlignCenter)
        layout.addWidget(textbox,0,1,Qt.AlignLeft)
        layout.addWidget(label1,1,0,Qt.AlignCenter)
        layout.addWidget(textbox1,1,1,Qt.AlignLeft)
        layout.addWidget(buttonOk,1,2,Qt.AlignCenter)
        layout.addWidget(table,0,3,3,2,Qt.AlignTop)
        layout.addWidget(tableRes,2,0,1,3,Qt.AlignBaseline)
        layout.addWidget(self.buttonGroup,2,3,Qt.AlignVCenter)

        layout.setHorizontalSpacing(50)
        layout.setVerticalSpacing(25)

        self.horizontalGroupBox.setLayout(layout)

    #Crea las columnas y filas de las dos tablas
    @staticmethod
    def createTables(self, table, tableRes, prod, restr, textbox, textbox1, buttonOk, buttonCalcular):
        if prod == "" or restr == "":
            self.showDialog("Ingrese la cantidad de producto y de restricciones!")
        else:
            #Convierte las cajas de texto en solo lectura
            textbox.setReadOnly(True)
            textbox1.setReadOnly(True)

            #Deshabilita el boton Ok
            buttonOk.setDisabled(True)
            buttonCalcular.setDisabled(False)

            #Tabla de valores
            table.setColumnCount(int(prod)+int(restr)+3)
            table.setRowCount(int(restr)+2)
            table.setItem(0,1, QTableWidgetItem("Cj"))
            table.setItem(1,0, QTableWidgetItem("Cb"))
            table.setItem(1,1, QTableWidgetItem("Xb"))

            #Vuelve las celdas que no reciben datos solo lectura
            delegate = ReadOnlyDelegate(table)
            table.setItemDelegateForRow(1, delegate)
            table.setItemDelegateForColumn(0, delegate)
            table.setItemDelegateForColumn(1, delegate)

            #tabla de resultados
            tableRes.setColumnCount(int(prod)+int(restr)+3)
            tableRes.setRowCount(int(restr)+4)
            tableRes.setItem(0,1, QTableWidgetItem("Cj"))
            tableRes.setItem(1,0, QTableWidgetItem("Cb"))
            tableRes.setItem(1,1, QTableWidgetItem("Xb"))
            tableRes.setItem(int(restr)+2,1, QTableWidgetItem("Zj"))
            tableRes.setItem(int(restr)+3,1, QTableWidgetItem("Cj-Zj"))

            #Asigna el formato a las celdas para insertar datos
            delegateNumber = NumberOnlyDelegate(table)
            table.setItemDelegateForRow(0, delegateNumber)
            
            row = 2
            while row <= int(restr)+1:
                table.setItemDelegateForRow(row, delegateNumber)

                row += 1

            i = 0
            j = 0
            x = 2
            y = 2
            while i < int(prod)+int(restr):
                table.setItem(1,x, QTableWidgetItem("X" + str(i+1)))
                tableRes.setItem(1,x, QTableWidgetItem("X" + str(i+1)))
                if i == (int(prod)+int(restr))-1:
                    table.setItem(1,x+1, QTableWidgetItem("Bi"))
                    tableRes.setItem(1,x+1, QTableWidgetItem("Bi"))
                i += 1 
                x += 1
                while j < int(restr):
                    table.setItem(y,0, QTableWidgetItem("0"))
                    table.setItem(y,1, QTableWidgetItem("X" + str(int(prod)+j+1)))
                    tableRes.setItem(y,0, QTableWidgetItem("0"))
                    tableRes.setItem(y,1, QTableWidgetItem("X" + str(int(prod)+j+1)))
                    j += 1
                    y += 1
            
            #Ajuste del ancho de las columnas
            for col in range(table.columnCount()):
                table.setColumnWidth(col, 50)
                tableRes.setColumnWidth(col, 100)

    #Calcula la primera tabla
    @staticmethod
    def calcular(self, table, tableRes, prod, restr, buttonCalcular, buttonSiguiente):
        camposVacios = True
        col = 2
        while col <= int(prod)+int(restr)+2:
            if col != int(prod)+int(restr)+2:
                if table.item(0, col):
                    if table.item(0, col).text() != '':
                        camposVacios = False
                    else:
                        camposVacios = True
                        break
                else:
                    camposVacios = True
                    break

            row = 2
            while row <= int(restr)+1:
                if table.item(row, col):
                    if table.item(row, col).text() != '':
                        camposVacios = False
                    else:   
                        camposVacios = True
                        break
                else:
                    camposVacios = True
                    break

                row += 1

            if camposVacios == True:
                break
            
            col += 1

        if camposVacios == False:
            global colPivot
            global filaPivot

            #Deshabilita la tabla inicial y el boton calcular
            table.setDisabled(True)
            buttonCalcular.setDisabled(True)

            #Habilita el boton siguiente
            buttonSiguiente.setDisabled(False)

            col = 2    
            while col <= int(prod)+int(restr)+2:
                if col != int(prod)+int(restr)+2:
                    tableRes.setItem(int(restr)+2, col, QTableWidgetItem("0"))
                    tableRes.setItem(0, col, QTableWidgetItem("{0:.7f}".format(float(table.item(0, col).text()))))
                    tableRes.setItem(int(restr)+3, col, QTableWidgetItem("{0:.7f}".format(float(table.item(0, col).text()))))

                row = 2
                while row <= int(restr)+1:
                    tableRes.setItem(row, col, QTableWidgetItem("{0:.7f}".format(float(table.item(row, col).text()))))

                    row += 1

                col += 1

            self.encontrarPivot(tableRes, prod, restr)
        else:
            self.showDialog("Faltan datos en algunos campos")
        
    #Encuntra la fila y columna pivot
    @staticmethod
    def encontrarPivot(tableRes, prod, restr):
        valoresCjZj = []
        valoresBi = []
        global colPivot
        global filaPivot

        col = 2    
        while col <= int(prod)+int(restr)+2:
            if col <= int(prod)+1: 
                valoresCjZj.append(float(tableRes.item(int(restr)+3, col).text()))

            col += 1

        columnaSaleValor = max(valoresCjZj)

        col = 2
        while col <= int(prod)+1:
            if float(tableRes.item(int(restr)+3, col).text()) == float(columnaSaleValor):
                colPivot = col
                break
            
            col += 1

        row = 2
        while row <= int(restr)+1:
            bi = float(tableRes.item(row, int(prod)+int(restr)+2).text())/float(tableRes.item(row, colPivot).text())
            valoresBi.append(bi)

            row += 1

        filaSaleValor = min(valoresBi)
        filaPivot = valoresBi.index(filaSaleValor)+2

        delegate = ReadOnlyDelegate(tableRes)

        for rows in range(tableRes.rowCount()):
            #Hace la tabla de solo lectura
            tableRes.setItemDelegateForRow(rows, delegate)
            #Marca los elementos de la fila pivot
            tableRes.item(rows, colPivot).setBackground(QtGui.QColor("deepskyblue"))
        
        for cols in range(tableRes.columnCount()):
            #Marca los elementos de la comlumna pivot
            tableRes.item(filaPivot, cols).setBackground(QtGui.QColor("deepskyblue"))

        tableRes.item(filaPivot, colPivot).setBackground(QtGui.QColor("cornflowerblue"))

    #Calcula la segunda tabla en adelante
    @staticmethod
    def calcularSiguiente(self, tableRes, prod, restr, buttonSiguiente, buttonNuevo):
        pivot = float(tableRes.item(filaPivot, colPivot).text())

        for rows in range(tableRes.rowCount()):
            tableRes.item(rows, colPivot).setBackground(QtGui.QColor("white"))
        
        for cols in range(tableRes.columnCount()):
            tableRes.item(filaPivot, cols).setBackground(QtGui.QColor("white"))

        tableRes.item(filaPivot, colPivot).setBackground(QtGui.QColor("white"))

        tableRes.setItem(filaPivot, 1, QTableWidgetItem(tableRes.item(1, colPivot).text()))
        tableRes.setItem(filaPivot, 0, QTableWidgetItem(tableRes.item(0, colPivot).text()))

        #Divide la columna pivot para el valor del pivot
        col = 2
        while col <= int(prod)+int(restr)+2:
            valorCelda = float(tableRes.item(filaPivot, col).text())
            valorNuevo = float(valorCelda/pivot)

            tableRes.setItem(filaPivot, col, QTableWidgetItem("{0:.7f}".format(valorNuevo)))
            
            col += 1

        #Obtiene los nuevos valores para el resto de la tabla
        row = 2
        while row <= int(restr)+1:
            col = 2
            if row != filaPivot:
                valorColPivot = float(tableRes.item(row, colPivot).text())
                while col <= int(prod)+int(restr)+2:
                    filaColPivot = valorColPivot*float(tableRes.item(filaPivot, col).text())
                    valorFilaAnterior = float(tableRes.item(row, col).text())
                    valorFilaNuevo = float(valorFilaAnterior - filaColPivot)

                    tableRes.setItem(row, col, QTableWidgetItem("{0:.7f}".format(valorFilaNuevo)))
                    
                    col +=1

            row += 1

        #Calcula los valores para zj
        col = 2
        while col <= int(prod)+int(restr)+2:
            zj = 0
            row = 2
            while row <= int(restr)+1:
                cb = float(tableRes.item(row, 0).text())
                xi = float(tableRes.item(row, col).text())
                xicb = cb*xi
                zj = zj+xicb

                row += 1

            tableRes.setItem(int(restr)+2, col, QTableWidgetItem("{0:.7f}".format(zj)))

            col += 1

        #Calcula los valores cj-zj
        col = 2
        while col <= int(prod)+int(restr)+1:
            cj = float(tableRes.item(0, col).text())
            zj = float(tableRes.item(int(restr)+2, col).text())

            cjMenosZj = cj - zj

            tableRes.setItem(int(restr)+3, col, QTableWidgetItem("{0:.7f}".format(cjMenosZj)))

            col += 1

        continuar = True
        col = 2
        while col <= int(prod)+2:
            valorCjMnsZj = float(tableRes.item(int(restr)+3, col).text())
            
            if valorCjMnsZj > 0:
                continuar = True
                break
            else:
                continuar = False
            
            col += 1

        if continuar == True:
            self.encontrarPivot(tableRes, prod, restr)
        else:
            buttonSiguiente.setDisabled(True)
            buttonNuevo.setDisabled(False)
            self.showDialog("Terminado!")

    #Reinicia el estado de la ventana
    @staticmethod
    def nuevoCalculo(textbox, textbox1, buttonOk, buttonNuevo, table, tableRes):
        #Se deshabilitan los widgets que ya no se utilizan
        buttonNuevo.setDisabled(True)

        #Se habilitan los widgets necesarios
        textbox.setReadOnly(False)
        textbox1.setReadOnly(False)
        buttonOk.setDisabled(False)
        table.setDisabled(False)

        #Se reinician las cajas de texto
        textbox.setText("")
        textbox1.setText("")

        #Se reinician las tablas
        table.setRowCount(0)
        table.setColumnCount(0)
        tableRes.setRowCount(0)
        tableRes.setColumnCount(0)

    #Muestra un mensaje de alerta cuando termina el proceso
    @staticmethod
    def showDialog(message):
        messgBox = QMessageBox()
        messgBox.setIcon(QMessageBox.Information)
        messgBox.setWindowTitle("Aviso")
        messgBox.setText(message)
        messgBox.setStandardButtons(QMessageBox.Ok)

        returnValue = messgBox.exec()

#
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())