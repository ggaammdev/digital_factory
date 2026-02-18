import logging
import sqlite3
import math
import random
from typing import Dict, List, Any

class FactoryState:
    """
    The Digital Twin of the Factory.
    Manages the state of the simulation: Inventory, Cash, Machine Health, Time.
    Now includes SQLite history and Dynamic Forecasting.
    """

    def __init__(self, db_path: str = "factory.db"):
        # --- Core State Variables ---
        self.inventory = 0  # Finished goods count
        self.cash_balance = 1000.0  # Starting capital ($)
        self.machine_health = 100.0  # % (0-100)
        
        # --- Time & Workforce ---
        self.factory_clock = 0  # Ticks (1 tick = 1 hour approx)
        self.current_shift = "DAY"  # DAY or NIGHT
        
        # --- Job Queue ---
        self.active_jobs: List[Dict] = []  # List of jobs currently running
        
        # --- Database ---
        self.db_path = db_path
        self._init_db()
        
        # --- Configuration ---
        self.base_market_price = 150.0
        self.base_market_demand = 10
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _init_db(self):
        """Initialize the SQLite database and tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # History Table: Logs state at every tick
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS factory_history (
                        tick INTEGER PRIMARY KEY,
                        cash_balance REAL,
                        inventory INTEGER,
                        machine_health REAL,
                        active_jobs_count INTEGER,
                        shift TEXT
                    )
                ''')
                
                # Jobs Table: Logs job details
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS job_history (
                        job_id TEXT PRIMARY KEY,
                        start_tick INTEGER,
                        end_tick INTEGER,
                        status TEXT,
                        revenue REAL,
                        cost REAL
                    )
                ''')
                conn.commit()
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")

    def _log_state(self):
        """Logs the current state to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO factory_history (tick, cash_balance, inventory, machine_health, active_jobs_count, shift)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (self.factory_clock, self.cash_balance, self.inventory, self.machine_health, len(self.active_jobs), self.current_shift))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to log state: {e}")

    def _log_job(self, job: Dict, status: str):
        """Logs a job update to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Upsert job (Insert or Replace if exists)
                cursor.execute('''
                    INSERT OR REPLACE INTO job_history (job_id, start_tick, end_tick, status, revenue, cost)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (job['id'], job['start_tick'], self.factory_clock, status, job.get('revenue', 0), job.get('cost', 0)))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to log job: {e}")

    # --- 1. Maintenance Logic ---
    def repair_machine(self) -> str:
        cost = 200
        if self.cash_balance >= cost:
            self.cash_balance -= cost
            self.machine_health = 100.0
            return f"Machine repaired. Cost: ${cost}. Health: 100%."
        else:
            return "Insufficient funds for repair."

    # --- 2. Finance Logic ---
    def start_job(self, job_id: str, qty: int) -> str:
        unit_cost = 50
        total_cost = unit_cost * qty
        
        if self.cash_balance >= total_cost:
            if self.machine_health <= 0:
                return "Machine broken. Cannot start job."
            
            self.cash_balance -= total_cost
            
            # Job Structure
            job = {
                "id": job_id,
                "qty": qty,
                "start_tick": self.factory_clock,
                "duration": 5, # Fixed duration for simplicity
                "cost": total_cost,
                "revenue": 0 # Will be calculated on completion
            }
            self.active_jobs.append(job)
            
            # Immediate wear (simplified)
            wear = 5 if self.current_shift == "DAY" else 8 # Night shift wear rule
            self.machine_health = max(0, self.machine_health - wear)
            
            self._log_job(job, "STARTED")
            return f"Job {job_id} started. Cost: ${total_cost}. Est. Duration: 5 ticks."
        else:
            return "Insufficient funds to start job."

    def cancel_job(self, job_id: str) -> str:
        for job in self.active_jobs:
            if job['id'] == job_id:
                self.active_jobs.remove(job)
                # No refund in this strict model
                self._log_job(job, "CANCELLED")
                return f"Job {job_id} cancelled."
        return "Job not found."

    # --- 3. Workforce Logic ---
    def change_shift(self, new_shift: str) -> str:
        if new_shift in ["DAY", "NIGHT"]:
            self.current_shift = new_shift
            return f"Shift changed to {new_shift}."
        return "Invalid shift. Use DAY or NIGHT."

    # --- 4. Forecasting Logic (Dynamic) ---
    def get_market_forecast(self, horizon: int = 5) -> Dict[str, Dict[str, Any]]:
        """
        Generates a dynamic market forecast using a sine wave model + noise.
        """
        forecast = {}
        for t in range(1, horizon + 1):
            future_tick = self.factory_clock + t
            
            # Sine wave model: Period of ~24 ticks (1 day)
            # Amplitude factor: 0.2 (fluctuates +/- 20%)
            cycle = math.sin(future_tick * (2 * math.pi / 24))
            
            # Demand: Base 10 + cycle * 5 + noise
            demand = int(self.base_market_demand + (cycle * 5) + random.randint(-2, 2))
            demand = max(1, demand) # Minimum demand 1
            
            # Price: Base 150 + cycle * 20 + noise
            # Price tends to be higher when demand is high (simplified correlation)
            price = self.base_market_price + (cycle * 20) + random.uniform(-5, 5)
            
            # Convert tick to string for JSON compatibility
            forecast[str(future_tick)] = {
                "demand": demand,
                "price": round(price, 2)
            }
        return forecast

    # --- Core Simulation Loop ---
    def tick(self):
        """
        Advances the simulation by one time step.
        Processes active jobs, updates state, and logs history.
        """
        self.factory_clock += 1
        
        # Process Jobs
        completed_jobs = []
        for job in self.active_jobs:
            job['duration'] -= 1
            if job['duration'] <= 0:
                completed_jobs.append(job)
        
        for job in completed_jobs:
            self.active_jobs.remove(job)
            
            # Revenue Calculation (Dynamic based on current market price)
            # For simplicity, we use the current tick's "spot price" from the forecast model
            current_market = self.get_market_forecast(horizon=1)[self.factory_clock + 1]
            market_price = current_market['price']
            
            revenue = job['qty'] * market_price
            job['revenue'] = revenue
            
            self.cash_balance += revenue
            self.inventory += job['qty']
            
            self._log_job(job, "COMPLETED")
            self.logger.info(f"Job {job['id']} completed. Revenue: ${revenue:.2f}")

        self._log_state()

    def get_status(self) -> str:
        return (f"Tick: {self.factory_clock} | Shift: {self.current_shift} | "
                f"Cash: ${self.cash_balance:.2f} | Inventory: {self.inventory} | "
                f"Health: {self.machine_health}% | Active Jobs: {len(self.active_jobs)}")
    
    def get_financials(self) -> Dict[str, float]:
        """Returns financial metrics."""
        return {
            "Cash Balance": self.cash_balance,
            "Unit Cost": 50, # Hardcoded for now as per start_job
            "Unit Revenue (Est)": self.base_market_price
        }

    def log_issue(self, category: str, description: str) -> str:
        """Logs an issue."""
        entry = f"[{category}] {description}"
        self.logger.warning(entry)
        return "LOGGED"
