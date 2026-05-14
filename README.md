# Sistema de Inteligencia Agrícola - UPN

Proyecto de **Análisis Numérico** que aplica dos métodos numéricos a problemas agrícolas:

- **Falsa Posición** → Cálculo del tirante hídrico óptimo de un canal de riego.
- **Bairstow** → Extracción de factores cuadráticos de un polinomio para predecir picos de cosecha.

El proyecto incluye tres componentes:

| Componente | Tecnología | Carpeta |
|---|---|---|
| Backend (API REST) | FastAPI + Pydantic | `reflex/video1/backend.py` |
| Frontend web | Reflex (Python → React) | `reflex/video1/` |
| App móvil Android | Flet (Python → Flutter) | `flet_app/` |

---

## Requisitos previos

Antes de empezar, asegúrate de tener instalado:

- **Python 3.12** (o superior)
- **Homebrew** (en macOS) — para instalar Flutter y Java
- **Git**

Para compilar el APK también necesitas:

- **Flutter SDK** → `brew install --cask flutter`
- **Java 17** → `brew install openjdk@17`
- **Android SDK** (con `cmdline-tools` y `platforms;android-36`)

---

## 1. Backend FastAPI (obligatorio)

Este servicio expone los dos métodos numéricos como endpoints HTTP. Es **requerido** para que tanto el frontend web como la app Android funcionen.

```bash
cd reflex/video1

# Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Levantar el servidor (escucha en todas las interfaces de red)
uvicorn backend:app --host 0.0.0.0 --port 8000
```

Verifica que el backend esté arriba abriendo `http://localhost:8000/docs` en el navegador (deberías ver la documentación Swagger).

### Endpoints disponibles

- `POST /agricola/falsa-posicion` — Calcula la profundidad óptima del canal.
- `POST /agricola/bairstow` — Extrae el factor cuadrático del polinomio.

---

## 2. Frontend web (Reflex)

Interfaz web con dos tarjetas: una para el cálculo de riego y otra para predicción de cosecha.

```bash
cd reflex/video1

# Si no creaste el venv en el paso anterior:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Inicializar Reflex (solo la primera vez)
reflex init

# Ejecutar
reflex run
```

Abre `http://localhost:3000` en el navegador.

> **Nota:** Reflex levanta su propio backend interno en el puerto 8001. El FastAPI debe seguir corriendo en el puerto 8000 simultáneamente para que los cálculos funcionen.

---

## 3. App móvil (Flet)

App Android que se conecta al backend FastAPI por HTTP.

### Probar en escritorio primero

```bash
cd flet_app

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Editar main.py línea 11:
# BACKEND_URL = "http://127.0.0.1:8000"

flet run main.py
```

### Compilar el APK para Android

**Paso 1 — Configurar la URL del backend**

Edita `flet_app/main.py:11` y ajusta `BACKEND_URL` según el caso:

| Destino | Valor de `BACKEND_URL` |
|---|---|
| Escritorio (`flet run`) | `http://127.0.0.1:8000` |
| Emulador Android | `http://10.0.2.2:8000` |
| Teléfono físico en la misma Wi-Fi | `http://<IP-LAN-de-tu-PC>:8000` |

Para obtener la IP LAN de tu Mac:
```bash
ipconfig getifaddr en0
```

**Paso 2 — Asegurar que el backend escucha en todas las interfaces**

```bash
cd reflex/video1
source .venv/bin/activate
uvicorn backend:app --host 0.0.0.0 --port 8000
```

> ⚠️ Importante: `--host 0.0.0.0` es esencial. Si usas `127.0.0.1`, el teléfono **no podrá conectarse**.

**Paso 3 — Construir el APK**

```bash
cd flet_app
source .venv/bin/activate

export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH="$JAVA_HOME/bin:$PATH"

flet build apk
```

La primera compilación tarda **10-15 minutos** (Gradle descarga dependencias de Android). Las siguientes son mucho más rápidas (2-3 min).

El APK queda en:
```
flet_app/build/apk/flet_app.apk
```

**Paso 4 — Instalar en el teléfono**

Opción A — Por USB con `adb`:
```bash
~/Library/Android/sdk/platform-tools/adb install -r flet_app/build/apk/flet_app.apk
```

Opción B — Transferencia manual: envía el archivo `.apk` por AirDrop / Drive / correo, ábrelo en el teléfono y permite la instalación de fuentes desconocidas si te lo pide.

---

## Estructura del proyecto

```
AnalisisNumerico/
├── code/
│   ├── Proyect##/          # Backend FastAPI inicial (referencia)
│   └── awesome-project/    # Scaffold inicial de FastAPI
├── flet_app/
│   ├── main.py             # App móvil (Flet)
│   └── requirements.txt
└── reflex/
    └── video1/
        ├── backend.py      # API FastAPI (producción)
        ├── app_reflex/     # Frontend web Reflex
        ├── rxconfig.py
        └── requirements.txt
```

---

## Solución de problemas

**El APK muestra una pantalla blanca:**
- La primera ejecución puede tardar 30-60 segundos en iniciar Python.
- Si persiste, conecta el teléfono por USB con depuración activada y ejecuta:
  ```bash
  ~/Library/Android/sdk/platform-tools/adb logcat -d --pid=$(adb shell pidof com.flet.flet_app)
  ```

**El teléfono no se conecta al backend:**
- Verifica que el teléfono y la PC estén en la **misma red Wi-Fi**.
- Confirma que `BACKEND_URL` en `main.py` apunta a la IP LAN correcta de la PC.
- Asegúrate de haber iniciado `uvicorn` con `--host 0.0.0.0`.
- Revisa que el firewall del sistema no esté bloqueando el puerto 8000.

**Error al construir el APK por Java:**
- Flet requiere JDK 17. Verifica con `java -version`.
- Si tienes otra versión, exporta `JAVA_HOME` apuntando a JDK 17 antes de ejecutar `flet build apk`.

---

## Créditos

Proyecto académico — **Universidad Tecnológica de Panamá / Universidad del Pacífico Norte** — Curso de Análisis Numérico.
