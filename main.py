import os
import sys
from state_engine import FactoryState
from tools import AFMTools
from agent import FactoryAgent

def load_system_instruction(path: str) -> str:
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: System instruction file not found at {path}")
        return "You are a helpful factory manager."

def main():
    print("Initializing Autonomous Factory Manager (AFM) v2.0...")
    
    # 1. Initialize Digital Twin (State Engine)
    state = FactoryState()
    
    # 2. Initialize Tools
    tools = AFMTools(state)
    
    # 3. Load System Instruction
    instruction_path = os.path.join(os.path.dirname(__file__), 'system_instruction.txt')
    system_instruction = load_system_instruction(instruction_path)
    
    # 4. Initialize Agent
    agent = FactoryAgent(tools, system_instruction)
    
    # Generate Session ID
    import uuid
    session_id = str(uuid.uuid4())
    user_id = "user_default"
    
    print("\n--- AFM System Ready ---")
    print(f"Session ID: {session_id}")
    print("Type 'exit' to quit.")
    print("Type 'status' to see the raw state engine status.")
    
    # 5. Interaction Loop
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            
            if user_input.lower() == 'status':
                print(f"DEBUG STATE: {state.get_status()}")
                continue
            
            # Delegate to Agent
            response = agent.send_message(user_input, user_id=user_id, session_id=session_id)
            print(f"AFM: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
