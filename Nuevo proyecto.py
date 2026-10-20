# Proyecto #2 INFO1157 - Simulacion 3D del sensor inercial BWT901CL
# Requiere: pip install vpython   (VPython 7, Python 3)
# Uso:      python proyecto2_inercial.py   (abre el navegador con la escena 3D)
#-----------------------------------------------------------------------------
from vpython import *
import ctypes as ct
import math, os

#-----------------------------------------------------------------------------
# Constantes globales
#-----------------------------------------------------------------------------
nMAX_G = 16                 # rango del giroscopo/acel. (no se usa para angulos)
nROLL, nPITCH, nYAW = 0, 1, 2
FILE   = 'inercial.bin'     # dejar en la misma carpeta que este script
FPS    = 50                 # cuadros por segundo de la animacion
LOOP   = True               # repetir la animacion al terminar el archivo

# Si el cubo gira al reves en algun eje (depende de como grabaron el video),
# cambie el signo de la constante correspondiente: 1 o -1
SGN = {nROLL: 1, nPITCH: 1, nYAW: 1}

#-----------------------------------------------------------------------------
# Trama del archivo: 11 bytes por paquete
#  0x55 | 0x53 | RollL RollH | PitchL PitchH | YawL YawH | TL TH | SUM
#-----------------------------------------------------------------------------
class eTrama(ct.Structure):
    _fields_ = [('B0', ct.c_ubyte), ('B1', ct.c_ubyte), ('B2', ct.c_ubyte),
                ('B3', ct.c_ubyte), ('B4', ct.c_ubyte), ('B5', ct.c_ubyte),
                ('B6', ct.c_ubyte), ('B7', ct.c_ubyte), ('B8', ct.c_ubyte),
                ('B9', ct.c_ubyte), ('BA', ct.c_ubyte)]

def Int16(nLow, nHigh):
    """Une dos bytes (little endian) en un entero con signo de 16 bits."""
    n = (nHigh << 8) | nLow
    return n - 65536 if n >= 32768 else n

def Lee_Angulos(sFile):
    """Lee todo el archivo y retorna una lista de (roll, pitch, yaw) en grados."""
    aAng = []
    with open(sFile, 'rb') as f:
        oT = eTrama()
        while f.readinto(oT) == ct.sizeof(oT):
            if oT.B0 != 0x55:                       # cabecera invalida
                continue
            nSum = sum(bytes(oT)[:10]) & 0xFF       # checksum
            if oT.B1 == 0x53 and nSum == oT.BA:     # 0x53 = paquete de angulos
                nR = Int16(oT.B2, oT.B3) / 32768.0 * 180.0
                nP = Int16(oT.B4, oT.B5) / 32768.0 * 180.0
                nY = Int16(oT.B6, oT.B7) / 32768.0 * 180.0
                aAng.append((nR, nP, nY))
    return aAng

#-----------------------------------------------------------------------------
# Definicion del Mundo 3D y sus Objetos
#-----------------------------------------------------------------------------
WinM = canvas(title='Sensor Inercial BWT901CL', width=1000, height=800,
              center=vector(0, 0, 0), background=color.black)
Base = box(pos=vector(0, -150, 0), size=vector(500, 3, 500), color=color.blue)

def Get_Frame(tFXYZ, nClr):
    """Cubo + ejes agrupados en un solo objeto (equivale al 'frame' antiguo)."""
    oB1 = box(pos=vector(0, 0, 0), size=vector(100, 60, 160), color=nClr)
    oB2 = box(pos=vector(0, 0, 0), size=vector(200, 2, 2),   color=color.blue)
    oB3 = box(pos=vector(0, 0, 0), size=vector(2, 200, 2),   color=color.green)
    oFr = compound([oB1, oB2, oB3], pos=vector(*tFXYZ))
    return oFr

#-----------------------------------------------------------------------------
# Rotaciones
# Ejes del sensor -> ejes de VPython (Y es "arriba" en VPython):
#   Roll  (giro sobre X del sensor) -> eje X
#   Pitch (giro sobre Y del sensor) -> eje -Z
#   Yaw   (giro sobre Z del sensor) -> eje Y
#-----------------------------------------------------------------------------
EJES = {nROLL: vector(1, 0, 0), nPITCH: vector(0, 0, -1), nYAW: vector(0, 1, 0)}

def Rota(nEje, nAng, xObj):
    """Rota el objeto 'nAng' grados sobre el eje nEje (eje fijo del mundo)."""
    xObj.rotate(angle=radians(SGN[nEje] * nAng), axis=EJES[nEje],
                origin=xObj.pos)

def Orienta(xObj, nR, nP, nY):
    """Deja el objeto en la orientacion absoluta (roll, pitch, yaw).
    Se parte siempre desde la pose inicial para no acumular error.
    Convencion del sensor: R = Rz(yaw) * Ry(pitch) * Rx(roll),
    por eso sobre ejes fijos se aplica primero roll, luego pitch, luego yaw."""
    xObj.axis = vector(1, 0, 0)
    xObj.up   = vector(0, 1, 0)
    Rota(nROLL,  nR, xObj)
    Rota(nPITCH, nP, xObj)
    Rota(nYAW,   nY, xObj)

#-----------------------------------------------------------------------------
# Codigo Main
#-----------------------------------------------------------------------------
sPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), FILE)
aAng  = Lee_Angulos(sPath)
print('Paquetes validos leidos:', len(aAng))

aObj = [Get_Frame((0, 0, 0), color.red)]
oLbl = label(pos=vector(0, 230, 0), text='', height=16, box=False,
             color=color.white)

while True:
    for i, (nR, nP, nY) in enumerate(aAng):
        rate(FPS)
        Orienta(aObj[0], nR, nP, nY)
        oLbl.text = 'Roll: %7.2f   Pitch: %7.2f   Yaw: %7.2f   [%d/%d]' % (
                    nR, nP, nY, i + 1, len(aAng))
    if not LOOP:
        break