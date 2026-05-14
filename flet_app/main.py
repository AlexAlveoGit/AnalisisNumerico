import flet as ft
import httpx

# ====================================================================
# CONFIGURACIÓN — Ajusta esta URL para que apunte a tu backend FastAPI.
# En el emulador Android se accede al host mediante 10.0.2.2.
# En un dispositivo físico, usa la IP LAN de la máquina que corre uvicorn,
# por ejemplo: "http://192.168.1.42:8000"
# ====================================================================
BACKEND_URL = "http://192.168.0.10:8000"


async def post_json(path: str, payload: dict) -> dict | None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{BACKEND_URL}{path}", json=payload)
        r.raise_for_status()
        return r.json()


def main(page: ft.Page):
    page.title = "Inteligencia Agrícola - UPN"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    # ---------- TAB 1: FALSA POSICIÓN ----------
    in_a = ft.TextField(label="Límite A", value="0", keyboard_type=ft.KeyboardType.NUMBER)
    in_b = ft.TextField(label="Límite B", value="4", keyboard_type=ft.KeyboardType.NUMBER)
    in_caudal = ft.TextField(label="Caudal objetivo (m³/s)", value="18", keyboard_type=ft.KeyboardType.NUMBER)
    out_riego = ft.Text("", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    tabla_riego = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Iter")),
            ft.DataColumn(ft.Text("Profundidad (m)")),
            ft.DataColumn(ft.Text("Error %")),
        ],
        rows=[],
    )
    btn_riego = ft.ElevatedButton(content="Calcular Riego", icon=ft.Icons.WATER_DROP, width=300)

    async def calcular_riego(e):
        out_riego.value = "Calculando..."
        tabla_riego.rows = []
        page.update()
        try:
            data = await post_json("/agricola/falsa-posicion", {
                "a": float(in_a.value),
                "b": float(in_b.value),
                "caudal": float(in_caudal.value),
                "tol": 0.001,
            })
            out_riego.value = f"Profundidad: {data['resultado']} m"
            for it in data.get("iteraciones", []):
                tabla_riego.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(it.get("iter", "")))),
                    ft.DataCell(ft.Text(str(it.get("profundidad_m", "")))),
                    ft.DataCell(ft.Text(str(it.get("error_pct", "")))),
                ]))
        except Exception as ex:
            out_riego.value = f"Error: {ex}"
        page.update()

    btn_riego.on_click = calcular_riego

    tab_riego = ft.Column(
        [
            ft.Text("Optimización de Riego", size=20, weight=ft.FontWeight.BOLD),
            in_caudal,
            ft.Row([in_a, in_b]),
            btn_riego,
            ft.Container(out_riego, padding=12, bgcolor=ft.Colors.BLUE_50, border_radius=8),
            ft.Container(tabla_riego, padding=4),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
    )

    # ---------- TAB 2: BAIRSTOW ----------
    in_coefs = ft.TextField(label="Coeficientes (ej: 1,-7,14,-8)", value="1,-7,14,-8")
    in_r = ft.TextField(label="Valor r", value="1.0", keyboard_type=ft.KeyboardType.NUMBER)
    in_s = ft.TextField(label="Valor s", value="1.0", keyboard_type=ft.KeyboardType.NUMBER)
    out_bairstow = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900)
    tabla_bairstow = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Iter")),
            ft.DataColumn(ft.Text("r")),
            ft.DataColumn(ft.Text("s")),
            ft.DataColumn(ft.Text("Error r")),
        ],
        rows=[],
    )
    btn_bairstow = ft.ElevatedButton(content="Predecir Producción", icon=ft.Icons.TRENDING_UP, width=300)

    async def calcular_bairstow(e):
        out_bairstow.value = "Calculando..."
        tabla_bairstow.rows = []
        page.update()
        try:
            coefs = [float(x.strip()) for x in in_coefs.value.split(",") if x.strip()]
            data = await post_json("/agricola/bairstow", {
                "coeficientes": coefs,
                "r": float(in_r.value),
                "s": float(in_s.value),
                "tol": 0.0001,
            })
            out_bairstow.value = f"Factor: {data['factor_hallado']}"
            for it in data.get("iteraciones", []):
                tabla_bairstow.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(it.get("iter", "")))),
                    ft.DataCell(ft.Text(str(it.get("r", "")))),
                    ft.DataCell(ft.Text(str(it.get("s", "")))),
                    ft.DataCell(ft.Text(str(it.get("error_r", "")))),
                ]))
        except Exception as ex:
            out_bairstow.value = f"Error: {ex}"
        page.update()

    btn_bairstow.on_click = calcular_bairstow

    tab_bairstow = ft.Column(
        [
            ft.Text("Predicción de Cosecha", size=20, weight=ft.FontWeight.BOLD),
            in_coefs,
            ft.Row([in_r, in_s]),
            btn_bairstow,
            ft.Container(out_bairstow, padding=12, bgcolor=ft.Colors.GREEN_50, border_radius=8),
            ft.Container(tabla_bairstow, padding=4),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
    )

    page.add(
        ft.SafeArea(
            ft.Column(
                [
                    ft.Container(
                        ft.Column(
                            [
                                ft.Text("Sistema de Inteligencia Agrícola - UPN", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Backend: {BACKEND_URL}", size=11, color=ft.Colors.GREY_700),
                            ],
                            spacing=2,
                        ),
                        padding=12,
                    ),
                    ft.Tabs(
                        length=2,
                        selected_index=0,
                        expand=True,
                        content=ft.Column(
                            expand=True,
                            controls=[
                                ft.TabBar(tabs=[
                                    ft.Tab(label="Riego", icon=ft.Icons.WATER_DROP),
                                    ft.Tab(label="Cosecha", icon=ft.Icons.TRENDING_UP),
                                ]),
                                ft.TabBarView(
                                    expand=True,
                                    controls=[
                                        ft.Container(tab_riego, padding=12),
                                        ft.Container(tab_bairstow, padding=12),
                                    ],
                                ),
                            ],
                        ),
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
