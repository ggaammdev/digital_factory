from typing import List, Dict, Any
from state_engine import FactoryState

class AFMTools:
    """
    Defines the 8 strict tools for the Autonomous Factory Manager agent.
    These tools interact directly with the FactoryState (Digital Twin).
    """

    def __init__(self, state: FactoryState):
        self.state = state

    def start_job(self, order_id: str, qty: int) -> str:
        """
        Starts production. 
        Warning: Consumes Inventory & Cash. Damages Machine.
        
        Args:
            order_id: Unique identifier for the order.
            qty: Quantity to produce.
        """
        return self.state.start_job(order_id, qty)

    def cancel_job(self, order_id: str) -> str:
        """
        Stops a job immediately.
        
        Args:
            order_id: The ID of the job to cancel.
        """
        return self.state.cancel_job(order_id)

    def repair_machine(self) -> str:
        """
        Fixes the machine ($200 cost).
        Resets machine_health to 100.
        """
        return self.state.repair_machine()

    def change_shift(self) -> str:
        """
        Toggles DAY/NIGHT crews.
        Night shift causes more machine wear (-15%).
        """
        return self.state.change_shift()

    def get_status(self) -> Dict[str, Any]:
        """
        Returns snapshot of Health, Cash, Inventory, and Jobs.
        """
        return self.state.get_status()

    def get_financials(self) -> Dict[str, float]:
        """
        Returns Cash, Unit Cost ($50), and Unit Revenue ($150).
        """
        return self.state.get_financials()

    def get_market_forecast(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns list of products with high/low historical performance.
        Example: {"1": {"demand": 10, "price": 150}, ...}
        """
        return self.state.get_market_forecast()

    def log_issue(self, category: str, description: str) -> str:
        """
        Use for requests you cannot fulfill or to report issues.
        
        Args:
            category: The category of the issue (e.g., "ACCESS_DENIED").
            description: Details about the issue.
        """
        return self.state.log_issue(category, description)
