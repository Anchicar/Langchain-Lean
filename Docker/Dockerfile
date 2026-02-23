# Usamos una imagen que ya tenga Python y dependencias de sistema
FROM python:3.10-slim

# Instalar dependencias básicas
# git, curl, build-essential son vitales. 
# Añadimos wget y tar por si acaso.
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    tar \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar el gestor de versiones de Lean (elan) de forma desatendida (-y)
# Usamos una sola capa para instalar y configurar el PATH
RUN curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y --default-toolchain leanprover/lean4:v4.11.0

# Aseguramos que el binario de elan esté en el PATH para las siguientes instrucciones
ENV PATH="/root/.elan/bin:${PATH}"

# Verificar instalación
RUN elan --version && lean --version

# Crear un proyecto Lean de trabajo
WORKDIR /workspace

# Inicializamos un proyecto básico
RUN lake init my_lean_project

# Modificamos el lakefile para añadir mathlib
# Nota: Usamos una versión específica de mathlib si es posible, o 'git'
# Es importante que el nombre del package coincida (my_lean_project)
RUN echo 'require mathlib from git "https://github.com/leanprover-community/mathlib4" @ "v4.11.0"' >> lakefile.lean

# Forzamos el uso de la toolchain correcta creando el archivo
RUN echo "leanprover/lean4:v4.11.0" > lean-toolchain

# Actualizamos dependencias. Separamos esto para debug.
RUN lake update

# Intentamos obtener la caché. Si falla, no rompemos el build, pero avisamos.
# Mathlib es grande, y sin caché compilará lento, pero funcionará.
RUN lake exe cache get || echo "Advertencia: No se pudo descargar la caché de Mathlib. La compilación será lenta."

# Pre-compilar (opcional pero recomendado)
# RUN lake build

# Este comando mantiene el contenedor listo para recibir comandos
CMD ["/bin/bash"]