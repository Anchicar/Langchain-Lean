# Usamos una imagen que ya tenga Python y dependencias de sistema
FROM python:3.10-slim

# Instalar dependencias básicas
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar el gestor de versiones de Lean (elan)
RUN curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y
ENV PATH="/root/.elan/bin:${PATH}"

# Crear un proyecto Lean de trabajo
WORKDIR /workspace
RUN lake init my_lean_project

# Añadir Mathlib4 como dependencia
RUN echo 'require mathlib from git "https://github.com/leanprover-community/mathlib4"' >> lakefile.lean

# Descargar la versión de Lean especificada y pre-compilar Mathlib (esto tarda, pero es vital)
RUN lake update && lake exe cache get

# Este comando mantiene el contenedor listo para recibir comandos
CMD ["/bin/bash"]