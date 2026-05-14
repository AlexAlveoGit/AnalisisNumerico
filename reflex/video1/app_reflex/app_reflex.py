import reflex as rx
import httpx

# REEMPLAZA ESTA VARIABLE CON TU IP DE WSL
IP_WSL = "localhost" 

class State(rx.State):
    # --- Variables Falsa Posición ---
    limite_a: str = "0"
    limite_b: str = "4"
    caudal_objetivo: str = ""
    resultado_final: str = ""
    iteraciones: list[dict] = []
    
    # --- Variables Bairstow ---
    coeficientes_input: str = "1, -7, 14, -8" 
    valor_r: str = "1.0"
    valor_s: str = "1.0"
    resultado_bairstow: str = ""
    iteraciones_bairstow: list[dict] = []
    
    esta_cargando: bool = False

    def actualizar_caudal(self, valor: str): self.caudal_objetivo = valor
    def actualizar_a(self, valor: str): self.limite_a = valor
    def actualizar_b(self, valor: str): self.limite_b = valor
    def actualizar_coefs(self, valor: str): self.coeficientes_input = valor
    def actualizar_r(self, valor: str): self.valor_r = valor
    def actualizar_s(self, valor: str): self.valor_s = valor

    async def calcular_riego(self):
        if not self.caudal_objetivo:
            self.resultado_final = "Ingrese un caudal"
            return
        self.esta_cargando = True
        async with httpx.AsyncClient() as client:
            try:
                payload = {"a": float(self.limite_a), "b": float(self.limite_b), "caudal": float(self.caudal_objetivo), "tol": 0.001}
                url = f"http://{IP_WSL}:8000/agricola/falsa-posicion"
                response = await client.post(url, json=payload, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    self.resultado_final = f"{data['resultado']} m"
                    self.iteraciones = data.get("iteraciones", []) 
            except Exception: self.resultado_final = "Error de conexión"
            finally: self.esta_cargando = False

    async def calcular_produccion(self):
        self.esta_cargando = True
        async with httpx.AsyncClient() as client:
            try:
                coefs = [float(x.strip()) for x in self.coeficientes_input.split(",")]
                payload = {"coeficientes": coefs, "r": float(self.valor_r), "s": float(self.valor_s), "tol": 0.0001}
                url = f"http://{IP_WSL}:8000/agricola/bairstow"
                response = await client.post(url, json=payload, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    self.resultado_bairstow = data["factor_hallado"]
                    self.iteraciones_bairstow = data.get("iteraciones", [])
            except Exception: self.resultado_bairstow = "Error en datos"
            finally: self.esta_cargando = False

def input_field(label, placeholder, on_change, value=None):
    return rx.vstack(
        rx.text(label, size="2", weight="bold", color="#1f2937"),
        rx.input(
            placeholder=placeholder, value=value, on_change=on_change,
            color="black", variant="surface",
            style={"background-color": "white", "border_radius": "8px"}
        ),
        width="100%", align_items="start", spacing="1"
    )

def tabla_resultados(datos):
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Iter"), rx.table.column_header_cell("xl (a)"),
                    rx.table.column_header_cell("xu (b)"), rx.table.column_header_cell("xr (c)"),
                    rx.table.column_header_cell("Ea"),
                ),
            ),
            rx.table.body(
                rx.foreach(datos, lambda it: rx.table.row(
                    rx.table.cell(it["iter"]), rx.table.cell(it["a"]),
                    rx.table.cell(it["b"]), rx.table.cell(it["c"]),
                    rx.table.cell(it["fc"], color="#2563eb", weight="bold"),
                )),
            ),
            width="100%", variant="surface",
        ),
        style={"max_height": "200px", "overflow_y": "auto", "margin_top": "1em", "border_radius": "8px"}
    )

def card_container(children, title, icon_name, icon_color):
    return rx.vstack(
        rx.hstack(rx.icon(icon_name, color=icon_color), rx.heading(title, size="4")),
        *children,
        padding="2em", bg="rgba(255, 255, 255, 0.9)", backdrop_filter="blur(10px)",
        border_radius="20px", box_shadow="lg", width="480px"
    )

def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Sistema de Inteligencia Agrícola - UPN", size="9", color="white", margin_bottom="1em"),
            
            rx.flex(
                # --- MÓDULO 1: RIEGO ---
                card_container([
                    input_field("Caudal Objetivo (m³/s)", "18", State.actualizar_caudal),
                    rx.hstack(
                        input_field("Límite A", "0", State.actualizar_a, State.limite_a),
                        input_field("Límite B", "4", State.actualizar_b, State.limite_b),
                    ),
                    rx.button("Calcular Riego", on_click=State.calcular_riego, width="100%", color_scheme="blue", loading=State.esta_cargando),
                    rx.box(
                        rx.text("Resultado:", size="1", weight="bold"),
                        rx.text(State.resultado_final, size="6", color="#1e40af", weight="bold"),
                        padding="0.8em", bg="#eff6ff", border_radius="10px"
                    ),
                    rx.cond(State.iteraciones, tabla_resultados(State.iteraciones)),
                ], "Cálculo de Tirante", "droplets", "#3b82f6"),

                # --- MÓDULO 2: PRODUCCIÓN ---
                card_container([
                    input_field("Coeficientes", "1, -7, 14, -8", State.actualizar_coefs, State.coeficientes_input),
                    rx.hstack(
                        input_field("Valor r", "1.0", State.actualizar_r, State.valor_r),
                        input_field("Valor s", "1.0", State.actualizar_s, State.valor_s),
                    ),
                    rx.button("Predecir Producción", on_click=State.calcular_produccion, width="100%", color_scheme="green", loading=State.esta_cargando),
                    rx.box(
                        rx.text("Factor Hallado:", size="1", weight="bold"),
                        rx.text(State.resultado_bairstow, size="5", color="#065f46", weight="bold"),
                        padding="0.8em", bg="#ecfdf5", border_radius="10px"
                    ),
                ], "Predicción de Cosecha", "trending-up", "#10b981"),
                
                spacing="6", # Espacio entre las tarjetas
                justify="center",
                flex_direction="row", # Esto asegura que estén uno al lado del otro
            ),
            padding_y="4em"
        ),
        width="100%", min_height="100vh",
        background_image="url('/fondo_riego.jpg')", background_size="cover", background_attachment="fixed",
    )

app = rx.App()
app.add_page(index)