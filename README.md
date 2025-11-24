# 🏃 Pipeline Analytics - Media Maratón La Serena 2024

[![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.8.1-017CEE?logo=apache-airflow)](https://airflow.apache.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📖 Descripción

Pipeline de datos **end-to-end** para procesar y analizar los resultados de la Media Maratón La Serena 2024. Este proyecto implementa la **Arquitectura Medallón** (Bronze-Silver-Gold) orquestada con **Apache Airflow** y containerizada con **Docker**.

--

## 🎯 Problema que Resuelve

Los datos de carreras suelen venir en formatos "sucios":
- Campos concatenados (`"Varones 30 a 39 añosdorsal: 2395"`)
- Formatos inconsistentes de tiempo
- Nombres mal capitalizados
- Sin métricas calculadas

Este pipeline automatiza la limpieza y genera **KPIs listos para análisis**.

---

## 🏗️ Arquitectura

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    BRONZE    │────▶│    SILVER    │────▶│     GOLD     │────▶│  VALIDACIÓN  │
│   Ingesta    │     │   Limpieza   │     │     KPIs     │     │    Final     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
      │                    │                    │
      ▼                    ▼                    ▼
  CSV crudo           Datos limpios      5 archivos de KPIs
  25 registros        + métricas         para dashboards
```

### Capas del Pipeline

| Capa | Input | Output | Descripción |
|------|-------|--------|-------------|
| **Bronze** | Simulación | `resultados_raw.csv` | Datos crudos tal como vienen de la fuente |
| **Silver** | Bronze CSV | `resultados_clean.csv` | Datos limpios, tipados, con métricas calculadas |
| **Gold** | Silver CSV | 5 archivos de KPIs | Agregaciones listas para consumo de negocio |

---

## 📊 KPIs Generados (Capa Gold)

1. **`kpi_estadisticas_generales.csv`** - Resumen de la carrera
2. **`kpi_tiempo_por_categoria.csv`** - Promedios por categoría
3. **`kpi_top5_por_genero.csv`** - Mejores 5 varones y damas
4. **`kpi_distribucion_edad.csv`** - Participantes por rango de edad
5. **`kpi_top10_ritmo.csv`** - Los 10 corredores más rápidos

---

## 🚀 Inicio Rápido

### Prerrequisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado
- [Git](https://git-scm.com/) (opcional)
- 4GB RAM mínimo disponible

### Paso 1: Clonar/Crear el proyecto

```bash
# Crear estructura de carpetas
mkdir -p media_maraton_pipeline/{dags,scripts,data/{bronze,silver,gold},logs}
cd media_maraton_pipeline

# Crear archivo __init__.py
touch scripts/__init__.py
```

### Paso 2: Crear los archivos

Copia el contenido de los siguientes archivos del tutorial:
- `docker-compose.yaml`
- `Dockerfile`
- `requirements.txt`
- `dags/media_maraton_dag.py`
- `scripts/pipeline_tasks.py`

### Paso 3: Levantar el entorno

```bash
# Construir la imagen (solo la primera vez o si cambias requirements.txt)
docker compose build

# Levantar todos los servicios
docker compose up -d

# Verificar que todo esté corriendo
docker compose ps
```

### Paso 4: Acceder a Airflow

1. Abre tu navegador en **http://localhost:8080**
2. Login: `admin` / `admin`
3. Busca el DAG: `pipeline_media_maraton_la_serena_2024`
4. Actívalo con el toggle (ON)
5. Haz clic en **"Trigger DAG"** ▶️

### Paso 5: Verificar resultados

```bash
# Ver los archivos generados
ls -la data/bronze/
ls -la data/silver/
ls -la data/gold/

# Ver contenido de un KPI
cat data/gold/kpi_estadisticas_generales.csv
```

---

## 📁 Estructura del Proyecto

```
media_maraton_pipeline/
│
├── dags/
│   └── media_maraton_dag.py    # Definición del workflow Airflow
│
├── scripts/
│   ├── __init__.py             # Hace de scripts un paquete Python
│   └── pipeline_tasks.py       # Lógica de negocio (Bronze/Silver/Gold)
│
├── data/
│   ├── bronze/                 # Datos crudos
│   │   └── resultados_raw.csv
│   ├── silver/                 # Datos limpios
│   │   └── resultados_clean.csv
│   └── gold/                   # KPIs
│       ├── kpi_estadisticas_generales.csv
│       ├── kpi_tiempo_por_categoria.csv
│       ├── kpi_top5_por_genero.csv
│       ├── kpi_distribucion_edad.csv
│       └── kpi_top10_ritmo.csv
│
├── logs/                       # Logs de Airflow
├── docker-compose.yaml         # Orquestación de contenedores
├── Dockerfile                  # Imagen personalizada
├── requirements.txt            # Dependencias Python
└── README.md                   # Este archivo
```

---

## 🔧 Comandos Útiles

```bash
# Ver logs de un servicio específico
docker compose logs -f airflow-scheduler

# Reiniciar Airflow (si cambias código en dags/)
docker compose restart airflow-scheduler airflow-webserver

# Detener todo
docker compose down

# Detener y eliminar volúmenes (reset completo)
docker compose down -v

# Entrar a un contenedor para debugging
docker compose exec airflow-scheduler bash

# Ejecutar el pipeline manualmente desde CLI
docker compose exec airflow-scheduler airflow dags trigger pipeline_media_maraton_la_serena_2024
```

---

## 🐛 Troubleshooting

### El DAG no aparece en la UI
```bash
# Verificar errores de sintaxis
docker compose exec airflow-scheduler python /opt/airflow/dags/media_maraton_dag.py

# Ver logs del scheduler
docker compose logs airflow-scheduler | grep -i error
```

### Error de importación de módulos
```bash
# Verificar que PYTHONPATH esté configurado
docker compose exec airflow-scheduler echo $PYTHONPATH
# Debe mostrar: /opt/airflow/scripts
```

### La base de datos no inicializa
```bash
# Reiniciar el init
docker compose down -v
docker compose up -d
```

---
## 📸 Capturas 

### DAG Cargado Correctamente en Airflow

### Vista Graph del Pipeline

![Graph](media_maraton_pipeline/dags/Airflow_graph.png)

---

## 📈 Próximos Pasos (Ideas para extender)

- [ ] Conectar a datos reales via API
- [ ] Agregar tests con pytest
- [ ] Implementar alertas de Slack
- [ ] Crear dashboard en Streamlit/Metabase
- [ ] Añadir capa de Data Quality con Great Expectations
- [ ] Migrar a cloud (AWS MWAA, GCP Composer)

---

## 👨‍💻 Autor

**Tu Nombre** - *Marcelo Rivera Vega*

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 🙏 Agradecimientos

- Organizadores de la Media Maratón La Serena
- Comunidad de Apache Airflow

---

*¿Te fue útil este proyecto? ¡Dale una ⭐ y compártelo!*
