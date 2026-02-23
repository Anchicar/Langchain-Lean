import sys
import os

# Agregamos el directorio raíz al path para poder importar langchain_lean
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_lean.core.environment import LeanEnvironmentManager
from langchain_lean.tools.repl_tool import LeanREPLTool

def test_environment():
    print("--- 1. Probando LeanEnvironmentManager ---")
    try:
        # Esto intentará conectarse a Docker
        env_manager = LeanEnvironmentManager()
        print("✅ Conexión con Docker exitosa.")
        
        print("Intentando aprovisionar el entorno (esto puede tardar si tiene que bajar la imagen)...")
        env_manager.provision_environment()
        print("✅ Entorno aprovisionado correctamente.")
        
    except Exception as e:
        print(f"❌ Error en EnvironmentManager: {e}")

def test_tool():
    print("\n--- 2. Probando LeanREPLTool ---")
    try:
        tool = LeanREPLTool()
        print(f"✅ Herramienta creada: {tool.name}")
        print(f"Descripción: {tool.description[:50]}...")
        
        # Probamos una ejecución simple (aunque el evaluador aún no está completo)
        code = "def hello : String := \"world\""
        print(f"Ejecutando código de prueba:\n{code}")
        
        # Esto fallará o dará un resultado vacío porque evaluator.py no está terminado,
        # pero verificará que la infraestructura de clases funciona.
        result = tool.run(code)
        print(f"Resultado de la herramienta: {result}")
        
    except Exception as e:
        print(f"❌ Error al ejecutar la herramienta: {e}")

if __name__ == "__main__":
    test_environment()
    test_tool()
