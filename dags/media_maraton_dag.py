"""
media_maraton_dag.py - VERSIÓN CON IMPORTS CORREGIDOS
======================================================
"""

from datetime import datetime, timedelta
from airflow.decorators import dag, task

default_args = {
    'owner': 'data_engineering_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'email_on_failure': False,
    'email_on_retry': False,
    'depends_on_past': False,
}


@dag(
    dag_id='pipeline_media_maraton_la_serena_2024',
    default_args=default_args,
    description='Pipeline ETL Media Maratón La Serena 2024',
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'media_maraton', 'medallion_architecture', 'tutorial'],
)
def pipeline_media_maraton():
    
    @task(task_id='bronze_ingesta')
    def bronze_task() -> str:
        """Ejecuta el proceso de ingesta Bronze."""
        import sys
        import os
        from pathlib import Path
        
        # Añadimos /opt/airflow al path (padre de scripts/)
        airflow_home = Path('/opt/airflow')
        if str(airflow_home) not in sys.path:
            sys.path.insert(0, str(airflow_home))
        
        # También añadimos scripts/ directamente
        scripts_path = airflow_home / 'scripts'
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))
        
        # Cambiar al directorio correcto
        os.chdir(str(airflow_home))
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"📂 Working directory: {os.getcwd()}")
        logger.info(f"📂 sys.path includes: {[p for p in sys.path if 'airflow' in p]}")
        logger.info(f"📂 scripts exists: {scripts_path.exists()}")
        logger.info(f"📂 Files in scripts: {list(scripts_path.glob('*.py'))}")
        
        # Intentar importación
        try:
            from scripts.pipeline_tasks import process_bronze
            logger.info("✅ Import exitoso!")
        except ImportError as e:
            logger.error(f"❌ Error de importación: {e}")
            # Intento alternativo: importación directa
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "pipeline_tasks", 
                str(scripts_path / "pipeline_tasks.py")
            )
            pipeline_tasks = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pipeline_tasks)
            process_bronze = pipeline_tasks.process_bronze
            logger.info("✅ Import alternativo exitoso!")
        
        return process_bronze()
    
    
    @task(task_id='silver_limpieza')
    def silver_task(bronze_file: str) -> str:
        """Ejecuta el proceso de limpieza Silver."""
        import sys
        import os
        from pathlib import Path
        
        airflow_home = Path('/opt/airflow')
        scripts_path = airflow_home / 'scripts'
        
        if str(airflow_home) not in sys.path:
            sys.path.insert(0, str(airflow_home))
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))
        
        os.chdir(str(airflow_home))
        
        try:
            from scripts.pipeline_tasks import process_silver
        except ImportError:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "pipeline_tasks", 
                str(scripts_path / "pipeline_tasks.py")
            )
            pipeline_tasks = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pipeline_tasks)
            process_silver = pipeline_tasks.process_silver
        
        return process_silver(bronze_file)
    
    
    @task(task_id='gold_kpis')
    def gold_task(silver_file: str) -> dict:
        """Ejecuta el proceso de agregación Gold."""
        import sys
        import os
        from pathlib import Path
        
        airflow_home = Path('/opt/airflow')
        scripts_path = airflow_home / 'scripts'
        
        if str(airflow_home) not in sys.path:
            sys.path.insert(0, str(airflow_home))
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))
        
        os.chdir(str(airflow_home))
        
        try:
            from scripts.pipeline_tasks import process_gold
        except ImportError:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "pipeline_tasks", 
                str(scripts_path / "pipeline_tasks.py")
            )
            pipeline_tasks = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pipeline_tasks)
            process_gold = pipeline_tasks.process_gold
        
        return process_gold(silver_file)
    
    
    @task(task_id='validacion_final')
    def validacion_task(gold_outputs: dict) -> str:
        """Validación final del pipeline"""
        import logging
        from pathlib import Path
        
        logger = logging.getLogger(__name__)
        logger.info("🔍 Validando outputs...")
        
        archivos_validos = 0
        archivos_faltantes = []
        
        for nombre, ruta in gold_outputs.items():
            if Path(ruta).exists():
                archivos_validos += 1
                logger.info(f"✅ {nombre}: OK")
            else:
                archivos_faltantes.append(nombre)
                logger.warning(f"❌ {nombre}: NO ENCONTRADO")
        
        total = len(gold_outputs)
        
        if archivos_validos == total:
            mensaje = f"🎉 Pipeline completado exitosamente! {total}/{total} archivos generados."
            logger.info(mensaje)
        else:
            mensaje = f"⚠️ Pipeline con errores: {archivos_validos}/{total} archivos. Faltantes: {archivos_faltantes}"
            logger.warning(mensaje)
        
        return mensaje
    
    
    # Flujo del pipeline
    bronze_output = bronze_task()
    silver_output = silver_task(bronze_output)
    gold_outputs = gold_task(silver_output)
    validacion_task(gold_outputs)


dag_instance = pipeline_media_maraton()