from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import math

app = FastAPI(title="Sistema de Inteligencia Agrícola - UPN")

# --- MODELOS DE DATOS ---
class FalsaPosicionInput(BaseModel):
    a: float  # Límite inferior (ej: 0)
    b: float  # Límite superior (ej: 4)
    caudal: float # Caudal objetivo (ej: 10)
    tol: float # Tolerancia (ej: 0.001)

class BairstowInput(BaseModel):
    coeficientes: List[float] # Ejemplo: [6, -5, 1] para x^2 - 5x + 6
    r: float # Valor inicial r (ej: 1.0)
    s: float # Valor inicial s (ej: -1.0)
    tol: float # Tolerancia (ej: 0.01)

# --- METODO 1: FALSA POSICION (OPTIMIZACION DE RIEGO) ---
@app.post("/agricola/falsa-posicion")
def metodo_falsa_posicion(data: FalsaPosicionInput):
    # f(y) representa el balance entre la forma del canal y el caudal
    def f(y): return y**3 - data.caudal
    
    a, b = data.a, data.b
    iteraciones = []
    xr = a
    
    for i in range(1, 15):
        xr_old = xr
        # Formula de Falsa Posicion: interpolacion lineal
        xr = b - (f(b) * (a - b)) / (f(a) - f(b))
        
        error = abs((xr - xr_old) / xr) * 100 if xr != 0 else 0
        iteraciones.append({
            "iter": i,
            "profundidad_m": round(xr, 4),
            "error_pct": round(error, 4)
        })
        
        if abs(f(xr)) < data.tol or error < data.tol:
            break
            
        if f(a) * f(xr) < 0:
            b = xr
        else:
            a = xr
            
    return {
        "metodo": "Falsa Posicion",
        "tema": "Optimización de Riego",
        "analisis": "Cálculo de tirante hídrico para canales en Panamá Oeste",
        "parametros": {"caudal_objetivo": data.caudal},
        "resultado_final_metros": round(xr, 4),
        "iteraciones": iteraciones,
        "explicacion": f"Se determino que la profundidad optima del canal debe ser de {round(xr, 4)} metros."
    }

# --- METODO 2: BAIRSTOW (PREDICCION DE PRODUCCION) ---
@app.post("/agricola/bairstow")
def metodo_bairstow(data: BairstowInput):
    # Bairstow extrae factores cuadraticos de modelos de crecimiento polinomial
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
        iteraciones.append({"iter": k, "r": round(r, 4), "s": round(s, 4), "error_r": round(error, 4)})
        
        if error < data.tol: break

    return {
        "metodo": "Bairstow",
        "tema": "Predicción de Producción",
        "analisis": "Extracción de factores de maduración de cultivos",
        "iteraciones": iteraciones,
        "factor_hallado": f"x^2 - ({round(r,4)})x - ({round(s,4)})",
        "explicacion": "Las raíces de este factor cuadrático definen los puntos de máxima cosecha."
    }
