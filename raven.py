import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
import os

def cargar_imagen_base64(ruta_imagen):
    """Carga la imagen de la ruta y la convierte a Base64."""
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    else:
        st.error(f"No se encontró la imagen en la ruta: {ruta_imagen}")
        return None

class AplicacionPC:
    def __init__(self, ruta_excel, ruta_imagen1, ruta_imagen2):
        self.ruta_excel = ruta_excel
        self.ruta_imagen1 = ruta_imagen1
        self.ruta_imagen2 = ruta_imagen2
        self.datos = self.cargar_datos_excel()
        self.componentes_dict = {}
        self.precios_dict = {}
        self.mapeo_categorias = {
            'MOTHERBOARD': 'MB',
            'COOLER': 'COOLER',
            'CPU': 'CPU',
            'DISCO DURO': 'DISCO DURO',
            'MEM DDR': 'MEM DDR',
            'MONITOR': 'MONITOR',
            'MOUSE': 'MOUSE',
            'SSD': 'SSD',
            'TECLADO': 'TECLADO',
            'TARJETA DE VIDEO': 'TARJETA DE VIDEO'
        }
        if self.datos is not None:
            self.generar_diccionarios()

    def cargar_datos_excel(self):
        """Carga los datos del archivo Excel y maneja errores."""
        try:
            datos = pd.read_excel(self.ruta_excel)
            datos['COMPONENTES'] = datos['COMPONENTES'].ffill()
            datos = datos.dropna(subset=['ESPECIFICACIONES TECNICAS', 'COSTOS'])
            return datos
        except FileNotFoundError:
            st.error(f"No se encontró el archivo Excel en la ruta: {self.ruta_excel}")
            return None

    def generar_diccionarios(self):
        """Genera los diccionarios de componentes y precios a partir de los datos."""
        self.componentes_dict = {value: [] for value in self.mapeo_categorias.values()}
        self.precios_dict = {value: {} for value in self.mapeo_categorias.values()}

        for categoria_excel, categoria_app in self.mapeo_categorias.items():
            especificaciones = self.datos[self.datos['COMPONENTES'].str.contains(categoria_excel, na=False)]
            for _, fila in especificaciones.iterrows():
                self.componentes_dict[categoria_app].append(fila['ESPECIFICACIONES TECNICAS'])
                self.precios_dict[categoria_app][fila['ESPECIFICACIONES TECNICAS']] = fila['COSTOS']

    def mostrar_encabezado(self):
        """Muestra el encabezado y las imágenes en la aplicación."""
        imagen1_base64 = cargar_imagen_base64(self.ruta_imagen1)
        imagen2_base64 = cargar_imagen_base64(self.ruta_imagen2)

        if imagen1_base64 and imagen2_base64:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; background-color: #F0F0F0; padding: 10px; border-radius: 10px;">
                    <h1 style="color: #FF6347;">FINESI</h1>
                    <div style="text-align: center;">
                        <img src="data:image/png;base64,{imagen2_base64}" width="150" style="border-radius: 50%;">
                    </div>
                    <img src="data:image/png;base64,{imagen1_base64}" width="150" style="border-radius: 50%;">
                </div>
                """,
                unsafe_allow_html=True
            )

    def seleccionar_componentes(self):
        """Permite seleccionar componentes en la aplicación y calcula el costo total."""
        st.subheader("🔧 Selecciones de la PC")
        
        componentes_seleccionados = {}
        costo_total = 0

        for categoria, opciones in self.componentes_dict.items():
            st.markdown(f"""
            <style>
            .custom-selectbox .stSelectbox {{
                background-color: #282828;
                color: white;
                padding: 10px;
                border: 2px solid #FF6347;
                border-radius: 5px;
            }}
            </style>
            """, unsafe_allow_html=True)
            
            with st.container():
                st.markdown(f"<h3 style='color: #FF6347;'>{categoria}:</h3>", unsafe_allow_html=True)
                componente_seleccionado = st.selectbox(
                    f"Seleccione {categoria}", opciones, key=categoria, help="Selecciona un componente"
                )
                componentes_seleccionados[categoria] = componente_seleccionado
                costo_total += self.precios_dict[categoria].get(componente_seleccionado, 0)

        return componentes_seleccionados, costo_total

    def mostrar_costos(self, componentes_seleccionados, costo_total):
        """Muestra los costos de los componentes seleccionados y el costo total."""
        st.subheader("💸 Costo de componentes seleccionados")
        
        for categoria, componente in componentes_seleccionados.items():
            precio = self.precios_dict[categoria].get(componente, 0)
            st.markdown(f"""
            <div style="background-color: #282828; color: white; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                <h3 style="color: #FF6347;">{categoria}:</h3>
                <p><strong>{componente}</strong></p>
                <p><strong>Precio:</strong> ${precio:.2f}</p>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("💰 Costo total")
        st.write(f"### **Total: ${costo_total:.2f}**")

    def generar_recomendaciones(self, componentes):
        """Genera recomendaciones basadas en los componentes seleccionados."""
        recomendaciones = []
        
        if "i7" in componentes.get("CPU", ""):
            recomendaciones.append({
                "titulo": "Mejora de almacenamiento",
                "detalle": "Considera aumentar la capacidad del SSD para mejorar el rendimiento general de tu sistema, especialmente si ejecutas tareas exigentes.",
                "enlace": "https://www.techradar.com/best/best-ssd"
            })
        if "Ryzen 9" in componentes.get("CPU", ""):
            recomendaciones.append({
                "titulo": "Enfriamiento necesario",
                "detalle": "El Ryzen 9 es un procesador de alto rendimiento. Asegúrate de tener un buen sistema de enfriamiento para mantener temperaturas estables.",
                "enlace": "https://www.tomshardware.com/reviews/best-cpu-coolers,4181.html"
            })
        if "RTX 3080" in componentes.get("TARJETA DE VIDEO", ""):
            recomendaciones.append({
                "titulo": "Monitor adecuado",
                "detalle": "Un monitor de alta resolución complementará bien tu tarjeta gráfica RTX 3080. Esto te permitirá aprovechar al máximo su potencia gráfica.",
                "enlace": "https://www.pcgamer.com/best-4k-monitors-for-gaming/"
            })
        if "16GB" in componentes.get("MEM DDR", ""):
            recomendaciones.append({
                "titulo": "Aumenta la memoria RAM",
                "detalle": "Para tareas intensivas como edición de video o juegos, considera aumentar la memoria RAM a 32GB para mejorar el rendimiento.",
                "enlace": "https://www.techadvisor.com/buying-advice/pc-components/how-much-ram-do-you-need-3697201/"
            })

        return recomendaciones

    def mostrar_recomendaciones(self, recomendaciones):
        """Muestra las recomendaciones generadas de manera interactiva."""
        st.header("📋 Recomendaciones:")

        if recomendaciones:
            for rec in recomendaciones:
                with st.expander(rec['titulo']):
                    st.write(rec['detalle'])
                    st.markdown(f"[Leer más aquí]({rec['enlace']})")
        else:
            st.write("No hay recomendaciones adicionales.")

    def graficar_precios(self, componentes_seleccionados):
        """Genera una gráfica de los precios de los componentes seleccionados."""
        componentes = list(componentes_seleccionados.keys())
        precios = [self.precios_dict[comp].get(componentes_seleccionados[comp], 0) for comp in componentes]

        fig = go.Figure(go.Bar(
            x=precios,
            y=componentes,
            orientation='h',
            marker=dict(color='#FF6347'),
        ))
        fig.update_layout(
            title="Precios de los Componentes Seleccionados",
            xaxis_title="Precio ($)",
            yaxis_title="Componentes",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white")
        )
        st.plotly_chart(fig)

    def ejecutar(self):
        """Método principal para ejecutar la aplicación."""
        self.mostrar_encabezado()

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                componentes_seleccionados, costo_total = self.seleccionar_componentes()

            with col2:
                self.mostrar_costos(componentes_seleccionados, costo_total)

        recomendaciones = self.generar_recomendaciones(componentes_seleccionados)
        self.mostrar_recomendaciones(recomendaciones)
        self.graficar_precios(componentes_seleccionados)


ruta_excel = 'C:/Users/ADMIN/Desktop/Aplicacion_st-main/DATOS.xlsx'
ruta_imagen1 = 'C:/Users/ADMIN/Desktop/Aplicacion_st-main/raven.jpg'
ruta_imagen2 = 'C:/Users/ADMIN/Desktop/Aplicacion_st-main/images.png'

app = AplicacionPC(ruta_excel, ruta_imagen1, ruta_imagen2)
app.ejecutar()
