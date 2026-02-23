import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Importamos lo que hemos construido
from langchain_lean.tools.repl_tool import LeanREPLTool

def main():
    # 1. Configurar el LLM (GPT-4 es altamente recomendado para Lean 4)
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

    # 2. Inicializar nuestra herramienta
    # Esto activará el EnvironmentManager y verificará Docker
    lean_tool = LeanREPLTool()
    tools = [lean_tool]

    # 3. Definir el System Prompt
    # Aquí le damos al agente su "personalidad" de ingeniero formal
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Eres un experto en matemáticas formales y programación en Lean 4.
        Tu objetivo es demostrar teoremas matemáticos. 
        
        Sigue estos pasos:
        1. Escribe un bloque de código en Lean 4 para el teorema propuesto.
        2. Usa la herramienta 'lean_repl' para verificar tu código.
        3. Si la herramienta devuelve un error o metas pendientes (goals), corrige tu código y vuelve a intentarlo.
        4. No te des por vencido hasta que la herramienta confirme 'No goals' o 'Éxito'."""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 4. Crear el Agente
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True
    )

    # 5. El Desafío: Un teorema simple de inducción o propiedades de Nat
    print("\n--- INICIANDO AGENTE MATEMÁTICO ---")
    problem = """
    Demuestra el siguiente teorema en Lean 4:
    Para todo n : Nat, n + 0 = n.
    Utiliza una prueba por inducción o reflexión según corresponda.
    """
    
    result = agent_executor.invoke({"input": problem})
    
    print("\n--- RESULTADO FINAL ---")
    print(result["output"])

if __name__ == "__main__":
    # Asegúrate de tener tu API Key
    # os.environ["OPENAI_API_KEY"] = "tu_clave_aqui"
    main()