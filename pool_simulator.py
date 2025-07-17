#!/usr/bin/env python3
"""
HISA Ecosystem Simulator - Robust Pool Implementation with JSON Configuration
"""

import math
import random
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt

class HISAPool:
    """Class for HISA ecosystem pools with enhanced features"""
    def __init__(self, name, token, params):
        self.name = name
        self.token = token
        self.params = params
        self.total_staked = params.get("initial_staked", 0)
        self.historical_apy = []
        self.last_updated = datetime.now()
        self.transaction_history = []
    
    def calculate_apy(self, market_conditions):
        """Calculate dynamic APY based on pool type and market conditions"""
        base_apy = self.params.get("base_apy", 0)
        
        # Pool-specific APY calculations
        if "SDG_Impact" in self.name:
            sdg_boost = self.params.get("sdg_goals", 0) * 0.005
            impact_boost = market_conditions["sdg_impact_index"] * 0.08
            return base_apy + sdg_boost + impact_boost
        
        elif "Micro_REIT" in self.name:
            return base_apy + self.params.get("property_appreciation", 0)
        
        elif "Bamboo" in self.name:
            carbon_boost = (market_conditions["carbon_price"] / 50) * 0.1
            season_boost = 0.1 if self.params.get("rainy_season", False) else 0
            return (base_apy + carbon_boost) * (1 + season_boost)
        
        elif "Digital_Craftsmanship" in self.name:
            sales_boost = min(self.params.get("nft_sales", 0) / 50_000 * 0.04, 0.08)
            return base_apy + sales_boost
        
        elif "Water_Guardians" in self.name:
            water_boost = min(self.params.get("water_sources", 0) * 0.0005, 0.04)
            return base_apy + water_boost
        
        elif "Agroforestry" in self.name:
            return base_apy + (self.params.get("biodiversity_index", 0) * 0.12)
        
        elif "Oral_History" in self.name:
            minute_boost = min(self.params.get("minutes_preserved", 0) / 1000 * 0.03, 0.06)
            elder_bonus = 0.03 if self.params.get("elder_verified", False) else 0
            return base_apy + minute_boost + elder_bonus
        
        # Default APY calculation for other pools
        return base_apy + self.params.get("bonus_apy", 0)
    
    def update_pool_metrics(self, market_conditions):
        """Update pool metrics based on market conditions"""
        current_apy = self.calculate_apy(market_conditions)
        self.historical_apy.append({
            "timestamp": datetime.now(),
            "apy": current_apy
        })
        self.last_updated = datetime.now()
        return current_apy
    
    def stake(self, amount, user_id=None):
        """Add tokens to the pool"""
        self.total_staked += amount
        transaction = {
            "type": "stake",
            "amount": amount,
            "timestamp": datetime.now(),
            "user_id": user_id
        }
        self.transaction_history.append(transaction)
        return transaction
    
    def unstake(self, amount, user_id=None):
        """Remove tokens from the pool"""
        if amount > self.total_staked:
            raise ValueError("Cannot unstake more than total staked")
        self.total_staked -= amount
        transaction = {
            "type": "unstake",
            "amount": amount,
            "timestamp": datetime.now(),
            "user_id": user_id
        }
        self.transaction_history.append(transaction)
        return transaction
    
    def to_dict(self):
        """Convert pool to dictionary for serialization"""
        return {
            "name": self.name,
            "token": self.token,
            "params": self.params,
            "total_staked": self.total_staked,
            "last_updated": self.last_updated.isoformat()
        }

class HISAEcosystem:
    """Core HISA Ecosystem Simulator with JSON configuration"""
    def __init__(self, config_path="hisa_config.json"):
        self.pools = {}
        self.market_conditions = {}
        self.user_portfolio = {}
        self.config_path = config_path
        self._load_configuration()
    
    def _load_configuration(self):
        """Load ecosystem configuration from JSON file"""
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Config file not found: {self.config_path}")
            
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Load market conditions
            self.market_conditions = config.get("market_conditions", {})
            
            # Create pools from configuration
            pools_config = config.get("pools", {})
            for token_category, pool_list in pools_config.items():
                for pool_config in pool_list:
                    pool = HISAPool(
                        name=pool_config["name"],
                        token=token_category,
                        params=pool_config
                    )
                    self.pools[pool_config["name"]] = pool
                    
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Fallback to default configuration
            self.market_conditions = {
                "crypto_volatility": 0.65,
                "community_engagement": 0.78,
                "carbon_price": 42.50,
                "sdg_impact_index": 0.72
            }
    
    def save_configuration(self):
        """Save current configuration to JSON file"""
        try:
            config = {
                "market_conditions": self.market_conditions,
                "pools": {}
            }
            
            # Organize pools by token category
            for pool in self.pools.values():
                token = pool.token
                if token not in config["pools"]:
                    config["pools"][token] = []
                
                config["pools"][token].append({
                    "name": pool.name,
                    **pool.params
                })
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def update_market_conditions(self):
        """Simulate changing market conditions"""
        self.market_conditions["crypto_volatility"] = max(0.1, min(0.95, 
            self.market_conditions["crypto_volatility"] + random.uniform(-0.1, 0.1)))
        
        self.market_conditions["carbon_price"] = max(35, min(65, 
            self.market_conditions["carbon_price"] + random.uniform(-2, 2)))
        
        self.market_conditions["community_engagement"] = max(0.4, min(0.99, 
            self.market_conditions["community_engagement"] + random.uniform(-0.05, 0.05)))
        
        # Update seasonal conditions
        rainy_season = datetime.now().month in [3, 4, 5, 10, 11]
        bamboo_pool = self.pools.get("JANI_Bamboo_Futures")
        if bamboo_pool:
            bamboo_pool.params["rainy_season"] = rainy_season
    
    # ... (other methods remain similar with JSON integration) ...

class HISACLI:
    """Enhanced CLI with JSON configuration management"""
    # ... (previous CLI methods) ...
    
    def edit_configuration(self):
        """Edit pool parameters through the CLI"""
        self.list_pools()
        try:
            pool_choice = int(input("\nSelect a pool to configure: "))
            pool_names = list(self.ecosystem.pools.keys())
            
            if 1 <= pool_choice <= len(pool_names):
                pool_name = pool_names[pool_choice - 1]
                pool = self.ecosystem.pools[pool_name]
                
                print(f"\nEditing {pool_name}:")
                print(f"Current parameters: {json.dumps(pool.params, indent=2)}")
                
                print("\nAvailable parameters to edit:")
                for i, param in enumerate(pool.params.keys(), 1):
                    print(f"{i}. {param}: {pool.params[param]}")
                
                param_choice = int(input("\nSelect parameter to edit: "))
                param_names = list(pool.params.keys())
                
                if 1 <= param_choice <= len(param_names):
                    param_name = param_names[param_choice - 1]
                    new_value = input(f"Enter new value for {param_name} (current: {pool.params[param_name]}): ")
                    
                    # Convert to appropriate type
                    if isinstance(pool.params[param_name], float):
                        new_value = float(new_value)
                    elif isinstance(pool.params[param_name], int):
                        new_value = int(new_value)
                    elif isinstance(pool.params[param_name], bool):
                        new_value = new_value.lower() in ['true', '1', 'yes']
                    
                    pool.params[param_name] = new_value
                    
                    # Save configuration
                    if self.ecosystem.save_configuration():
                        print("✅ Configuration updated and saved!")
                    else:
                        print("❌ Error saving configuration")
                else:
                    print("Invalid parameter selection")
            else:
                print("Invalid pool selection")
        except Exception as e:
            print(f"Error: {e}")

# Run the simulator
if __name__ == "__main__":
    cli = HISACLI()