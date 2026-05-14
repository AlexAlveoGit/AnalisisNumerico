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

> 📌 Esta guía está escrita para **Windows 10/11**. Todos los comandos usan **PowerShell** (la terminal recomendada). Si usas CMD clásico, los comandos de activación de entornos virtuales y exportación de variables son ligeramente distintos — se indica donde aplica.

---

## Requisitos previos

Antes de empezar, asegúrate de tener instalado:

- **Python 3.12** o superior → [python.org/downloads](https://www.python.org/downloads/)
  - ⚠️ Durante la instalación marca la casilla **"Add Python to PATH"**.
- **Git para Windows** → [git-scm.com](https://git-scm.com/download/win)

Para **compilar el APK** también necesitas:

- **Flutter SDK** → [docs.flutter.dev/get-started/install/windows](https://docs.flutter.dev/get-started/install/windows)
- **JDK 17** (Temurin/Adoptium) → [adoptium.net](https://adoptium.net/temurin/releases/?version=17)
- **Android Studio** (incluye el Android SDK y `cmdline-tools`) → [developer.android.com/studio](https://developer.android.com/studio)
  - Después de instalar, abre Android Studio → **More Actions → SDK Manager** y asegúrate de tener instalado:
    - **Android SDK Platform 36**
    - **Android SDK Command-line Tools (latest)**
    - **Android SDK Build-Tools**
    - **Android SDK Platform-Tools**

---

## 1. Backend FastAPI (obligatorio)

Este servicio expone los dos métodos numéricos como endpoints HTTP. Es **requerido** para que tanto el frontend web como la app Android funcionen.

```powershell
cd reflex\video1

# Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# Si PowerShell te da error de "execution policy", ejecútalo una sola vez:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# Instalar dependencias
pip install -r requirements.txt

# Levantar el servidor (escucha en todas las interfaces de red)
uvicorn backend:app --host 0.0.0.0 --port 8000
```

> En **CMD clásico**, la activación del venv es: `.venv\Scripts\activate.bat`

Verifica que el backend esté arriba abriendo `http://localhost:8000/docs` en el navegador (deberías ver la documentación Swagger).

### Endpoints disponibles

- `POST /agricola/falsa-posicion` — Calcula la profundidad óptima del canal.
- `POST /agricola/bairstow` — Extrae el factor cuadrático del polinomio.

---

## 2. Frontend web (Reflex)

Interfaz web con dos tarjetas: una para el cálculo de riego y otra para predicción de cosecha.

```powershell
cd reflex\video1

# Si no creaste el venv en el paso anterior:
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Inicializar Reflex (solo la primera vez)
reflex init

# Ejecutar
reflex run
```

Abre `http://localhost:3000` en el navegador.

> **Nota:** Reflex levanta su propio backend interno en el puerto 8001. El FastAPI debe seguir corriendo en el puerto 8000 simultáneamente para que los cálculos funcionen. Abre dos ventanas de PowerShell: una para el backend FastAPI y otra para Reflex.

---

## 3. App móvil (Flet)

App Android que se conecta al backend FastAPI por HTTP.

### Probar en escritorio primero

```powershell
cd flet_app

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Editar main.py línea 11:
# BACKEND_URL = "http://127.0.0.1:8000"

flet run main.py
```

### Compilar el APK para Android

**Paso 1 — Configurar la URL del backend**

Edita `flet_app\main.py` en la línea 11 y ajusta `BACKEND_URL` según el caso:

| Destino | Valor de `BACKEND_URL` |
|---|---|
| Escritorio (`flet run`) | `http://127.0.0.1:8000` |
| Emulador Android | `http://10.0.2.2:8000` |
| Teléfono físico en la misma Wi-Fi | `http://<IP-LAN-de-tu-PC>:8000` |

Para obtener la IP LAN de tu PC en PowerShell:
```powershell
ipconfig | Select-String "IPv4"
```

(Busca la línea correspondiente a tu adaptador **Wi-Fi** o **Ethernet**, por ejemplo `192.168.1.50`).

**Paso 2 — Asegurar que el backend escucha en todas las interfaces**

```powershell
cd reflex\video1
.venv\Scripts\Activate.ps1
uvicorn backend:app --host 0.0.0.0 --port 8000
```

> ⚠️ Importante: `--host 0.0.0.0` es esencial. Si usas `127.0.0.1`, el teléfono **no podrá conectarse**.

La primera vez que ejecutes esto, Windows Defender puede preguntarte si quieres permitir que Python acepte conexiones entrantes — **acepta** para que el teléfono pueda conectarse.

**Paso 3 — Configurar variables de entorno para la compilación**

En la **misma ventana de PowerShell** donde compilarás (antes de ejecutar `flet build apk`):

```powershell
# Ajusta las rutas según donde estén instalados JDK 17 y el Android SDK
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.13.11-hotspot"
$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"

# Verificar que apunten a las versiones correctas
java -version
flutter doctor
```

> En **CMD clásico**, usa: `set JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-17.0.13.11-hotspot`

**Paso 4 — Construir el APK**

```powershell
cd flet_app
.venv\Scripts\Activate.ps1

flet build apk
```

La primera compilación tarda **10-15 minutos** (Gradle descarga dependencias de Android). Las siguientes son mucho más rápidas (2-3 min).

El APK queda en:
```
flet_app\build\apk\flet_app.apk
```

**Paso 5 — Instalar en el teléfono**

Opción A — Por USB con `adb` (requiere habilitar **Depuración USB** en Opciones de desarrollador):
```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r flet_app\build\apk\flet_app.apk
```

Opción B — Transferencia manual: envía el archivo `.apk` por correo, WhatsApp, Google Drive o cable USB al teléfono, ábrelo y permite la instalación de fuentes desconocidas si te lo pide.

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

**PowerShell rechaza la activación del venv ("execution of scripts is disabled"):**
- Ejecuta una sola vez (con PowerShell normal, no como admin):
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  ```

**El APK muestra una pantalla blanca:**
- La primera ejecución puede tardar 30-60 segundos en iniciar Python.
- Si persiste, conecta el teléfono por USB con depuración activada y ejecuta:
  ```powershell
  $adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
  & $adb logcat -d --pid=(& $adb shell pidof com.flet.flet_app)
  ```

**El teléfono no se conecta al backend:**
- Verifica que el teléfono y la PC estén en la **misma red Wi-Fi**.
- Confirma que `BACKEND_URL` en `main.py` apunta a la IP LAN correcta de la PC (usa `ipconfig` para verificarla).
- Asegúrate de haber iniciado `uvicorn` con `--host 0.0.0.0`.
- Revisa que **Windows Defender Firewall** no esté bloqueando Python en el puerto 8000. Cuando levantas el backend por primera vez, Windows te pregunta si permitir el acceso — acepta para **redes privadas**.

**Error al construir el APK por Java:**
- Flet requiere JDK 17. Verifica con:
  ```powershell
  java -version
  ```
- Si tienes otra versión instalada, ajusta `$env:JAVA_HOME` apuntando a JDK 17 antes de ejecutar `flet build apk`.

**`flutter doctor` indica que faltan componentes:**
- Abre Android Studio → **SDK Manager** y asegúrate de instalar lo listado en los requisitos previos.
- Acepta las licencias del Android SDK:
  ```powershell
  flutter doctor --android-licenses
  ```

---

## Créditos

Proyecto académico — **Universidad Tecnológica de Panamá / Universidad del Pacífico Norte** — Curso de Análisis Numérico.
