"""
pipeline_tasks.py
=================
Funciones de procesamiento para el Pipeline Media Maratón La Serena 2024.

Este módulo implementa la arquitectura Medallón (Bronze → Silver → Gold)
con funciones puras, bien documentadas y con manejo de errores.

Autor: Marcelo Rivera Vega
Fecha: 2025
"""

import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

import pandas as pd

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE LOGGING
# ─────────────────────────────────────────────────────────────
# Configuramos el logger para este módulo.
# Esto nos permite rastrear qué está pasando en cada paso del pipeline.
# En producción, estos logs son INVALUABLES para debugging.

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE RUTAS
# ─────────────────────────────────────────────────────────────
# Usamos pathlib.Path porque:
# 1. Es multiplataforma (Windows, Linux, Mac)
# 2. Ofrece métodos útiles como .exists(), .mkdir(), etc.
# 3. Se puede concatenar con / de forma elegante

# La base es /opt/airflow dentro del contenedor Docker
BASE_PATH = Path("/opt/airflow/data")
BRONZE_PATH = BASE_PATH / "bronze"
SILVER_PATH = BASE_PATH / "silver"
GOLD_PATH = BASE_PATH / "gold"


# ─────────────────────────────────────────────────────────────
# CAPA BRONZE: INGESTA DE DATOS CRUDOS
# ─────────────────────────────────────────────────────────────

def process_bronze() -> str:
    """
    Capa Bronze: Ingesta de datos crudos.
    
    En un escenario real, aquí podrías:
    - Descargar archivos de un SFTP
    - Consultar una API externa
    - Leer de un bucket S3
    
    Para este tutorial, simulamos la ingesta creando el archivo
    con datos "sucios" tal como vendrían del mundo real.
    
    Returns:
        str: Ruta del archivo creado en la capa Bronze.
        
    Raises:
        Exception: Si hay un error al crear el archivo.
    """
    logger.info("🥉 Iniciando proceso BRONZE - Ingesta de datos crudos")
    
    try:
        # Creamos el directorio si no existe
        # parents=True crea directorios padres si faltan
        # exist_ok=True no lanza error si ya existe
        BRONZE_PATH.mkdir(parents=True, exist_ok=True)
        
        # ─────────────────────────────────────────────────
        # DATOS SIMULADOS - Tal como vendrían del "mundo real"
        # ─────────────────────────────────────────────────
        # Observa los problemas que tenemos que resolver:
        # 1. "Categoría" y "Dorsal" están pegados en una sola celda
        # 2. Algunos nombres están en minúsculas
        # 3. El formato del tiempo es string "H:MM:SS"
        # 4. Las posiciones tienen el símbolo "º"
        
        raw_data = [
            # [Pos General, Pos Categoría, Nombre, Categoría+Dorsal, Tiempo]
            ["1º", "1º", "Carlos Andrés Díaz Moreno", "Varones 18 a 29 añosdorsal: 2001", "1:12:45"],
            ["2º", "1º", "Miguel Ángel Torres", "Varones 30 a 39 añosdorsal: 2102", "1:15:22"],
            ["3º", "2º", "Juan Pablo Soto Vera", "Varones 18 a 29 añosdorsal: 2015", "1:16:08"],
            ["4º", "2º", "Roberto Carlos Muñoz", "Varones 30 a 39 añosdorsal: 2156", "1:18:33"],
            ["5º", "1º", "Andrea Paz González", "Damas 18 a 29 añosdorsal: 2201", "1:19:45"],
            ["15º", "3º", "Pedro José Ramírez", "Varones 30 a 39 añosdorsal: 2178", "1:25:12"],
            ["22º", "1º", "María José Pérez Silva", "Damas 30 a 39 añosdorsal: 2245", "1:28:56"],
            ["35º", "1º", "Francisco Javier López", "Varones 40 a 49 añosdorsal: 2301", "1:32:18"],
            ["48º", "2º", "Carmen Gloria Fuentes", "Damas 30 a 39 añosdorsal: 2267", "1:35:44"],
            ["56º", "4º", "Andrés Felipe Castillo", "Varones 30 a 39 añosdorsal: 2189", "1:37:22"],
            ["72º", "2º", "Patricia Andrea Núñez", "Damas 40 a 49 añosdorsal: 2312", "1:40:15"],
            ["89º", "5º", "Diego Alejandro Vera", "Varones 30 a 39 añosdorsal: 2195", "1:42:58"],
            ["127º", "47º", "Abel Ballon Aguirre", "Varones 30 a 39 añosdorsal: 2395", "1:46:32"],
            ["145º", "3º", "Claudia Marcela Rojas", "Damas 40 a 49 añosdorsal: 2334", "1:49:18"],
            ["171º", "43º", "Alberto Ignacio Salas Nicolau", "Varones 40 a 49 añosdorsal: 2296", "1:52:08"],
            ["198º", "12º", "Valentina Paz Morales", "Damas 18 a 29 añosdorsal: 2223", "1:55:42"],
            ["215º", "8º", "José Manuel Contreras", "Varones 50 a 59 añosdorsal: 2401", "1:58:15"],
            ["234º", "4º", "Rosa Elena Martínez", "Damas 40 a 49 añosdorsal: 2356", "2:02:33"],
            ["256º", "15º", "Sergio Antonio Pizarro", "Varones 50 a 59 añosdorsal: 2418", "2:06:48"],
            ["266º", "19º", "alexandrina vivar diaz", "Damas 40 a 49 añosdorsal: 2084", "2:09:40"],
            ["278º", "1º", "Manuel Eduardo Lagos", "Varones 60+ añosdorsal: 2501", "2:12:22"],
            ["289º", "5º", "Isabel Cristina Araya", "Damas 50 a 59 añosdorsal: 2445", "2:15:55"],
            ["301º", "2º", "Héctor Raúl Mendoza", "Varones 60+ añosdorsal: 2512", "2:20:18"],
            ["315º", "1º", "Teresa de Jesús Campos", "Damas 60+ añosdorsal: 2521", "2:25:42"],
            ["328º", "6º", "Gabriela Fernanda Ríos", "Damas 50 a 59 añosdorsal: 2467", "2:30:15"],
        ]
        
        # Creamos el DataFrame con nombres de columnas descriptivos
        # pero que reflejan el "problema" de la data cruda
        df_raw = pd.DataFrame(
            raw_data,
            columns=[
                "pos_general",
                "pos_categoria", 
                "nombre_corredor",
                "categoria_dorsal",  # ¡Este es el campo problemático!
                "tiempo_oficial"
            ]
        )
        
        # Guardamos como CSV (simulando el archivo que recibiríamos)
        output_file = BRONZE_PATH / "resultados_raw.csv"
        df_raw.to_csv(output_file, index=False)
        
        logger.info(f"✅ Bronze completado: {len(df_raw)} registros guardados en {output_file}")
        
        # Retornamos la ruta como string para que Airflow pueda pasarla entre tareas
        return str(output_file)
        
    except Exception as e:
        # Logueamos el error con nivel ERROR para fácil identificación
        logger.error(f"❌ Error en proceso Bronze: {str(e)}")
        # Re-lanzamos la excepción para que Airflow marque la tarea como fallida
        raise


# ─────────────────────────────────────────────────────────────
# CAPA SILVER: LIMPIEZA Y TRANSFORMACIÓN
# ─────────────────────────────────────────────────────────────

def _parse_categoria_dorsal(texto: str) -> tuple[str, str, str, Optional[int]]:
    """
    Función auxiliar para parsear el campo 'categoria_dorsal'.
    
    Esta función usa REGEX (expresiones regulares) para extraer:
    - Género (Varones/Damas)
    - Rango de edad (ej: "30 a 39 años")
    - Número de dorsal
    
    Args:
        texto: String con formato "Varones 30 a 39 añosdorsal: 2395"
        
    Returns:
        Tupla con (genero, rango_edad, categoria_completa, dorsal)
        
    Ejemplo:
        >>> _parse_categoria_dorsal("Varones 30 a 39 añosdorsal: 2395")
        ('Varones', '30 a 39 años', 'Varones 30 a 39 años', 2395)
    """
    # ─────────────────────────────────────────────────
    # EXPLICACIÓN DEL REGEX
    # ─────────────────────────────────────────────────
    # ^(Varones|Damas)  → Captura "Varones" o "Damas" al inicio
    # \s+               → Uno o más espacios
    # (.+?)             → Captura el rango de edad (non-greedy con ?)
    # dorsal:\s*        → La palabra "dorsal:" seguida de espacios opcionales
    # (\d+)             → Captura uno o más dígitos (el número de dorsal)
    # $                 → Fin del string
    
    pattern = r'^(Varones|Damas)\s+(.+?)dorsal:\s*(\d+)$'
    
    match = re.match(pattern, texto, re.IGNORECASE)
    
    if match:
        genero = match.group(1).capitalize()  # "varones" → "Varones"
        rango_edad = match.group(2).strip()   # Removemos espacios extra
        dorsal = int(match.group(3))          # Convertimos a entero
        categoria_completa = f"{genero} {rango_edad}"
        
        return genero, rango_edad, categoria_completa, dorsal
    else:
        # Si el regex no hace match, retornamos valores por defecto
        logger.warning(f"⚠️ No se pudo parsear: {texto}")
        return "Desconocido", "Desconocido", texto, None


def _tiempo_a_segundos(tiempo_str: str) -> int:
    """
    Convierte un tiempo en formato "H:MM:SS" a segundos totales.
    
    Esto es útil para:
    1. Hacer cálculos matemáticos (promedios, diferencias)
    2. Ordenar correctamente los tiempos
    3. Comparar rendimientos
    
    Args:
        tiempo_str: Tiempo en formato "H:MM:SS" o "HH:MM:SS"
        
    Returns:
        Total de segundos como entero
        
    Ejemplo:
        >>> _tiempo_a_segundos("1:30:00")
        5400
    """
    partes = tiempo_str.split(':')
    
    if len(partes) == 3:
        horas, minutos, segundos = map(int, partes)
        return horas * 3600 + minutos * 60 + segundos
    elif len(partes) == 2:
        # Por si viene como "MM:SS" (menos de una hora)
        minutos, segundos = map(int, partes)
        return minutos * 60 + segundos
    else:
        logger.warning(f"⚠️ Formato de tiempo no reconocido: {tiempo_str}")
        return 0


def _calcular_ritmo(segundos_totales: int, distancia_km: float = 21.1) -> str:
    """
    Calcula el ritmo promedio (min/km) a partir del tiempo total.
    
    El ritmo es una métrica clave para corredores. Un maratonista
    elite corre a ~3:00 min/km, un amateur a ~6:00 min/km.
    
    Args:
        segundos_totales: Tiempo total de carrera en segundos
        distancia_km: Distancia de la carrera (21.1 km para media maratón)
        
    Returns:
        String con formato "M:SS" representando minutos por kilómetro
    """
    if segundos_totales <= 0 or distancia_km <= 0:
        return "0:00"
    
    segundos_por_km = segundos_totales / distancia_km
    minutos = int(segundos_por_km // 60)
    segundos = int(segundos_por_km % 60)
    
    return f"{minutos}:{segundos:02d}"


def process_silver(bronze_file: Optional[str] = None) -> str:
    """
    Capa Silver: Limpieza y transformación de datos.
    
    Esta es la capa donde ocurre la "magia" de la limpieza.
    Tomamos datos sucios y los convertimos en datos estructurados.
    
    Transformaciones aplicadas:
    1. Separar 'categoria_dorsal' en columnas individuales
    2. Limpiar posiciones (quitar 'º')
    3. Convertir tiempo a segundos para cálculos
    4. Calcular ritmo (min/km)
    5. Normalizar nombres (Title Case)
    
    Args:
        bronze_file: Ruta al archivo Bronze (opcional, usa default si no se pasa)
        
    Returns:
        str: Ruta del archivo creado en la capa Silver
    """
    logger.info("🥈 Iniciando proceso SILVER - Limpieza de datos")
    
    try:
        # Definimos rutas de entrada y salida
        input_file = Path(bronze_file) if bronze_file else BRONZE_PATH / "resultados_raw.csv"
        SILVER_PATH.mkdir(parents=True, exist_ok=True)
        output_file = SILVER_PATH / "resultados_clean.csv"
        
        # ─────────────────────────────────────────────────
        # PASO 1: Lectura del archivo Bronze
        # ─────────────────────────────────────────────────
        logger.info(f"📖 Leyendo archivo: {input_file}")
        df = pd.read_csv(input_file)
        logger.info(f"   Registros leídos: {len(df)}")
        
        # ─────────────────────────────────────────────────
        # PASO 2: Separar categoria_dorsal en columnas
        # ─────────────────────────────────────────────────
        # Usamos .apply() para aplicar nuestra función a cada fila
        # El resultado es una Serie de tuplas que expandimos con .tolist()
        
        logger.info("🔧 Parseando campo categoria_dorsal...")
        
        parsed_data = df['categoria_dorsal'].apply(_parse_categoria_dorsal)
        
        # Convertimos las tuplas a columnas separadas
        df['genero'] = parsed_data.apply(lambda x: x[0])
        df['rango_edad'] = parsed_data.apply(lambda x: x[1])
        df['categoria'] = parsed_data.apply(lambda x: x[2])
        df['dorsal'] = parsed_data.apply(lambda x: x[3])
        
        # Eliminamos la columna original (ya no la necesitamos)
        df = df.drop(columns=['categoria_dorsal'])
        
        # ─────────────────────────────────────────────────
        # PASO 3: Limpiar posiciones
        # ─────────────────────────────────────────────────
        # Removemos el símbolo "º" y convertimos a entero
        
        logger.info("🔧 Limpiando columnas de posición...")
        
        df['pos_general'] = df['pos_general'].str.replace('º', '').astype(int)
        df['pos_categoria'] = df['pos_categoria'].str.replace('º', '').astype(int)
        
        # ─────────────────────────────────────────────────
        # PASO 4: Normalizar nombres
        # ─────────────────────────────────────────────────
        # .str.title() convierte "JUAN PEREZ" o "juan perez" a "Juan Perez"
        
        logger.info("🔧 Normalizando nombres...")
        df['nombre_corredor'] = df['nombre_corredor'].str.title()
        
        # ─────────────────────────────────────────────────
        # PASO 5: Procesar tiempos
        # ─────────────────────────────────────────────────
        logger.info("🔧 Calculando métricas de tiempo...")
        
        df['tiempo_segundos'] = df['tiempo_oficial'].apply(_tiempo_a_segundos)
        df['ritmo_min_km'] = df['tiempo_segundos'].apply(_calcular_ritmo)
        
        # Calculamos la velocidad en km/h (otra métrica útil)
        df['velocidad_kmh'] = round(21.1 / (df['tiempo_segundos'] / 3600), 2)
        
        # ─────────────────────────────────────────────────
        # PASO 6: Reordenar columnas para mejor legibilidad
        # ─────────────────────────────────────────────────
        columnas_ordenadas = [
            'pos_general',
            'pos_categoria',
            'dorsal',
            'nombre_corredor',
            'genero',
            'rango_edad',
            'categoria',
            'tiempo_oficial',
            'tiempo_segundos',
            'ritmo_min_km',
            'velocidad_kmh'
        ]
        
        df = df[columnas_ordenadas]
        
        # ─────────────────────────────────────────────────
        # PASO 7: Guardar resultado
        # ─────────────────────────────────────────────────
        df.to_csv(output_file, index=False)
        
        logger.info(f"✅ Silver completado: {len(df)} registros guardados en {output_file}")
        
        # Mostramos un preview de los datos limpios
        logger.info(f"📊 Preview de datos limpios:\n{df.head(3).to_string()}")
        
        return str(output_file)
        
    except FileNotFoundError:
        logger.error(f"❌ Archivo no encontrado: {input_file}")
        raise
    except Exception as e:
        logger.error(f"❌ Error en proceso Silver: {str(e)}")
        raise


# ─────────────────────────────────────────────────────────────
# CAPA GOLD: AGREGACIONES Y KPIs
# ─────────────────────────────────────────────────────────────

def process_gold(silver_file: Optional[str] = None) -> dict:
    """
    Capa Gold: Generación de KPIs y agregaciones de negocio.
    
    Aquí creamos las métricas que consumirían dashboards o reportes.
    Cada KPI se guarda como un archivo CSV separado.
    
    KPIs generados:
    1. Estadísticas generales de la carrera
    2. Tiempo promedio por categoría
    3. Top 5 más rápidos por género
    4. Distribución de participantes por rango de edad
    5. Top 10 mejores ritmos overall
    
    Args:
        silver_file: Ruta al archivo Silver (opcional)
        
    Returns:
        dict: Diccionario con las rutas de los archivos Gold generados
    """
    logger.info("🥇 Iniciando proceso GOLD - Generación de KPIs")
    
    try:
        # Definimos rutas
        input_file = Path(silver_file) if silver_file else SILVER_PATH / "resultados_clean.csv"
        GOLD_PATH.mkdir(parents=True, exist_ok=True)
        
        # Lectura de datos limpios
        logger.info(f"📖 Leyendo archivo: {input_file}")
        df = pd.read_csv(input_file)
        
        # Diccionario para almacenar rutas de archivos generados
        output_files = {}
        
        # ─────────────────────────────────────────────────
        # KPI 1: Estadísticas Generales
        # ─────────────────────────────────────────────────
        logger.info("📊 Generando KPI: Estadísticas Generales...")
        
        stats_generales = {
            'total_participantes': len(df),
            'total_varones': len(df[df['genero'] == 'Varones']),
            'total_damas': len(df[df['genero'] == 'Damas']),
            'tiempo_ganador': df['tiempo_oficial'].iloc[0],
            'tiempo_ultimo': df['tiempo_oficial'].iloc[-1],
            'tiempo_promedio_segundos': round(df['tiempo_segundos'].mean(), 2),
            'ritmo_promedio': _calcular_ritmo(int(df['tiempo_segundos'].mean())),
            'velocidad_promedio_kmh': round(df['velocidad_kmh'].mean(), 2),
            'fecha_proceso': datetime.now().isoformat()
        }
        
        df_stats = pd.DataFrame([stats_generales])
        stats_file = GOLD_PATH / "kpi_estadisticas_generales.csv"
        df_stats.to_csv(stats_file, index=False)
        output_files['estadisticas_generales'] = str(stats_file)
        
        # ─────────────────────────────────────────────────
        # KPI 2: Tiempo Promedio por Categoría
        # ─────────────────────────────────────────────────
        logger.info("📊 Generando KPI: Tiempo Promedio por Categoría...")
        
        # Agrupamos por categoría y calculamos métricas
        df_por_categoria = df.groupby('categoria').agg({
            'tiempo_segundos': ['mean', 'min', 'max', 'count'],
            'velocidad_kmh': 'mean'
        }).round(2)
        
        # Aplanamos los nombres de columnas multinivel
        df_por_categoria.columns = [
            'tiempo_promedio_seg', 
            'tiempo_mejor_seg', 
            'tiempo_peor_seg', 
            'cantidad_corredores',
            'velocidad_promedio_kmh'
        ]
        
        # Añadimos el ritmo promedio como columna legible
        df_por_categoria['ritmo_promedio'] = df_por_categoria['tiempo_promedio_seg'].apply(
            lambda x: _calcular_ritmo(int(x))
        )
        
        df_por_categoria = df_por_categoria.reset_index()
        
        categoria_file = GOLD_PATH / "kpi_tiempo_por_categoria.csv"
        df_por_categoria.to_csv(categoria_file, index=False)
        output_files['tiempo_por_categoria'] = str(categoria_file)
        
        # ─────────────────────────────────────────────────
        # KPI 3: Top 5 por Género
        # ─────────────────────────────────────────────────
        logger.info("📊 Generando KPI: Top 5 por Género...")
        
        # Top 5 Varones
        top_varones = df[df['genero'] == 'Varones'].nsmallest(5, 'tiempo_segundos')[
            ['pos_general', 'nombre_corredor', 'categoria', 'tiempo_oficial', 'ritmo_min_km']
        ]
        top_varones['ranking_genero'] = range(1, len(top_varones) + 1)
        
        # Top 5 Damas
        top_damas = df[df['genero'] == 'Damas'].nsmallest(5, 'tiempo_segundos')[
            ['pos_general', 'nombre_corredor', 'categoria', 'tiempo_oficial', 'ritmo_min_km']
        ]
        top_damas['ranking_genero'] = range(1, len(top_damas) + 1)
        
        # Combinamos en un solo archivo
        top_varones['genero'] = 'Varones'
        top_damas['genero'] = 'Damas'
        df_top_genero = pd.concat([top_varones, top_damas])
        
        top_file = GOLD_PATH / "kpi_top5_por_genero.csv"
        df_top_genero.to_csv(top_file, index=False)
        output_files['top5_por_genero'] = str(top_file)
        
        # ─────────────────────────────────────────────────
        # KPI 4: Distribución por Rango de Edad
        # ─────────────────────────────────────────────────
        logger.info("📊 Generando KPI: Distribución por Rango de Edad...")
        
        df_distribucion = df.groupby(['rango_edad', 'genero']).size().reset_index(name='cantidad')
        df_distribucion['porcentaje'] = round(
            df_distribucion['cantidad'] / len(df) * 100, 2
        )
        
        distribucion_file = GOLD_PATH / "kpi_distribucion_edad.csv"
        df_distribucion.to_csv(distribucion_file, index=False)
        output_files['distribucion_edad'] = str(distribucion_file)
        
        # ─────────────────────────────────────────────────
        # KPI 5: Top 10 Mejores Ritmos
        # ─────────────────────────────────────────────────
        logger.info("📊 Generando KPI: Top 10 Mejores Ritmos...")
        
        df_top_ritmo = df.nsmallest(10, 'tiempo_segundos')[
            ['pos_general', 'dorsal', 'nombre_corredor', 'categoria', 
             'tiempo_oficial', 'ritmo_min_km', 'velocidad_kmh']
        ]
        
        ritmo_file = GOLD_PATH / "kpi_top10_ritmo.csv"
        df_top_ritmo.to_csv(ritmo_file, index=False)
        output_files['top10_ritmo'] = str(ritmo_file)
        
        # ─────────────────────────────────────────────────
        # Resumen final
        # ─────────────────────────────────────────────────
        logger.info("✅ Gold completado. Archivos generados:")
        for nombre, ruta in output_files.items():
            logger.info(f"   📁 {nombre}: {ruta}")
        
        return output_files
        
    except FileNotFoundError:
        logger.error(f"❌ Archivo no encontrado: {input_file}")
        raise
    except Exception as e:
        logger.error(f"❌ Error en proceso Gold: {str(e)}")
        raise


# ─────────────────────────────────────────────────────────────
# FUNCIÓN DE PRUEBA LOCAL
# ─────────────────────────────────────────────────────────────
# Este bloque solo se ejecuta si corres el archivo directamente
# Es útil para testing local sin Airflow

if __name__ == "__main__":
    print("=" * 60)
    print("🏃 Pipeline Media Maratón La Serena 2024 - Test Local")
    print("=" * 60)
    
    # Para pruebas locales, ajustamos las rutas
    BASE_PATH = Path("./data")
    BRONZE_PATH = BASE_PATH / "bronze"
    SILVER_PATH = BASE_PATH / "silver"  
    GOLD_PATH = BASE_PATH / "gold"
    
    # Ejecutamos el pipeline completo
    print("\n[1/3] Ejecutando Bronze...")
    bronze_output = process_bronze()
    
    print("\n[2/3] Ejecutando Silver...")
    silver_output = process_silver(bronze_output)
    
    print("\n[3/3] Ejecutando Gold...")
    gold_outputs = process_gold(silver_output)
    
    print("\n" + "=" * 60)
    print("✅ Pipeline completado exitosamente!")
    print("=" * 60)

