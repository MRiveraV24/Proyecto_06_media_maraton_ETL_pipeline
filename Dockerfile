# Dockerfile
# Imagen personalizada de Airflow con nuestras dependencias
# =========================================================

# Usamos la imagen oficial de Airflow como base
# La versión slim es más ligera (sin extras innecesarios)
FROM apache/airflow:2.8.1-python3.11

# Cambiamos al usuario root temporalmente para instalar dependencias del sistema
# (si las necesitáramos, en este caso no, pero es buena práctica saberlo)
USER root

# Volvemos al usuario airflow por seguridad
# Airflow corre como usuario no-root por buenas prácticas de seguridad
USER airflow

# Copiamos nuestro archivo de dependencias
COPY requirements.txt /requirements.txt

# Instalamos las dependencias Python
# --no-cache-dir reduce el tamaño de la imagen
# --user instala en el directorio del usuario (evita problemas de permisos)
RUN pip install --no-cache-dir --user -r /requirements.txt
