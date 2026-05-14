from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import math

app = FastAPI(title="Sistema de Inteligencia Agrícola - UPN")

# --- CONFIGURACIÓN DE CORS ---
# Esto permite que tu frontend en Windows se comunique con el backend en Linux
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DATOS (DEFINIDOS PRIMERO) ---
# Se definen aquí para que los endpoints de abajo los reconozcan
class FalsaPosicionInput(BaseModel):
    a: float
    b: float
    caudal: float
    tol: float

class BairstowInput(BaseModel):
    coeficientes: List[float]
    r: float
    s: float
    tol: float

# --- MÉTODO 1: FALSA POSICIÓN (OPTIMIZACIÓN DE RIEGO) ---
@app.post("/agricola/falsa-posicion")
def metodo_falsa_posicion(data: FalsaPosicionInput):
    def f(y): return y**3 - data.caudal

    a, b = data.a, data.b
    iteraciones = []
    xr = a

    for i in range(1, 15):
        xr_old = xr
        f_a = f(a)
        f_b = f(b)

        if (f_a - f_b) == 0: break

        xr = b - (f_b * (a - b)) / (f_a - f_b)
        error = abs((xr - xr_old) / xr) * 100 if xr != 0 else 0

        iteraciones.append({
            "iter": str(i),
            "profundidad_m": str(round(xr, 4)),
            "error_pct": f"{round(error, 4)}%"
        })

        if abs(f(xr)) < data.tol or error < data.tol:
            break

        if f_a * f(xr) < 0:
            b = xr
        else:
            a = xr

    return {
        "resultado": round(xr, 4),
        "metodo": "Falsa Posición",
        "explicacion": f"La profundidad óptima es de {round(xr, 4)} metros.",
        "iteraciones": iteraciones
    }

# --- MÉTODO 2: BAIRSTOW (PREDICCIÓN DE COSECHA) ---
@app.post("/agricola/bairstow")
def metodo_bairstow(data: BairstowInput):
    a = data.coeficientes
    n = len(a) - 1
    r, s = data.r, data.s
    iteraciones = []

    for k in range(1, 11):
        b = [0] * (n + 1)
        c = [0] * (n + 1)

        b[n] = a[n]
        b[n-1] = a[n-1] + r*b[n]
        for i in range(n-2, -1, -1):
            b[i] = a[i] + r*b[i+1] + s*b[i+2]

        c[n] = b[n]
        c[n-1] = b[n-1] + r*c[n]
        for i in range(n-2, 1, -1): 
            c[i] = b[i] + r*c[i+1] + s*c[i+2]

        det = c[2]*c[2] - c[3]*c[1]
        if det == 0: break

        dr = (-b[1]*c[2] + b[0]*c[3]) / det
        ds = (-b[0]*c[2] + b[1]*c[1]) / det

        r += dr
        s += ds

        error = abs(dr/r)*100 if r != 0 else 0
        iteraciones.append({
            "iter": k,
            "r": round(r, 4),
            "s": round(s, 4),
            "error_r": round(error, 4)
        })

        if error < data.tol: break

    return {
        "metodo": "Bairstow",
        "tema": "Predicción de Producción",
        "analisis": "Extracción de factores de maduración de cultivos",
        "iteraciones": iteraciones,
        "factor_hallado": f"x^2 - ({round(r,4)})x - ({round(s,4)})",
        "explicacion": "Las raíces de este factor cuadrático definen los puntos de máxima cosecha."
    }