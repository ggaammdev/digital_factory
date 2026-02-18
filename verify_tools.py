from state_engine import FactoryState
from tools import AFMTools
import json

def verify_tools():
    print("Initializing State Engine and Tools...")
    state = FactoryState()
    tools = AFMTools(state)
    
    print("Testing get_market_forecast...")
    forecast = tools.get_market_forecast()
    print(f"Forecast keys: {list(forecast.keys())}")
    
    # Verify keys are strings
    all_strings = all(isinstance(k, str) for k in forecast.keys())
    if all_strings:
        print("SUCCESS: All keys are strings.")
    else:
        print("FAILURE: Some keys are not strings.")
        
    # Verify JSON serialization (simulating ADK behavior)
    try:
        json_output = json.dumps(forecast)
        print("SUCCESS: JSON serialization worked.")
    except Exception as e:
        print(f"FAILURE: JSON serialization failed: {e}")

if __name__ == "__main__":
    verify_tools()
