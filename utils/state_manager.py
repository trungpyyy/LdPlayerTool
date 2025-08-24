"""
State Manager for Rise of Kingdoms Tool
Manages saving and restoring application state including device tasks and pause states
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import config

logger = logging.getLogger(__name__)

class StateManager:
    """Manages application state persistence and restoration"""
    
    def __init__(self, state_file: str = None):
        self.state_file = state_file or config.STATE_FILE_PATH
        self.state = {
            "last_updated": "",
            "devices": {},
            "global_settings": {
                "default_pause_state": config.DEFAULT_PAUSE_STATE,  # Use config default
                "last_device": None,
                "window_position": None
            }
        }
        self._ensure_data_directory()
        self.load_state()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        data_dir = os.path.dirname(self.state_file)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created data directory: {data_dir}")
    
    def load_state(self) -> bool:
        """Load state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    loaded_state = json.load(f)
                    # Merge with default state to handle missing keys
                    self._merge_state(loaded_state)
                    logger.info(f"State loaded from {self.state_file}")
                    return True
            else:
                logger.info("No existing state file found, using defaults")
                return False
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return False
    
    def save_state(self) -> bool:
        """Save current state to file"""
        try:
            self.state["last_updated"] = datetime.now().isoformat()
            
            # Ensure data directory exists
            self._ensure_data_directory()
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            
            logger.info(f"State saved to {self.state_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            return False
    
    def _merge_state(self, loaded_state: Dict[str, Any]):
        """Merge loaded state with default state"""
        if "devices" in loaded_state:
            self.state["devices"].update(loaded_state["devices"])
        
        if "global_settings" in loaded_state:
            self.state["global_settings"].update(loaded_state["global_settings"])
    
    def get_device_state(self, device_id: str) -> Dict[str, Any]:
        """Get state for a specific device"""
        return self.state["devices"].get(device_id, {
            "tasks": {},
            "pause_state": True,  # Default to paused
            "farm_priority": ["food", "wood", "stone", "gold"],
            "current_farm_index": 0,
            "last_used": None
        })
    
    def save_device_state(self, device_id: str, **kwargs):
        """Save state for a specific device"""
        if device_id not in self.state["devices"]:
            self.state["devices"][device_id] = {}
        
        self.state["devices"][device_id].update(kwargs)
        self.state["devices"][device_id]["last_used"] = datetime.now().isoformat()
        
        # Auto-save when device state changes
        self.save_state()
    
    def save_device_tasks(self, device_id: str, tasks: Dict[str, Any]):
        """Save task configuration for a device"""
        self.save_device_state(device_id, tasks=tasks)
    
    def save_device_pause_state(self, device_id: str, is_paused: bool):
        """Save pause state for a device"""
        self.save_device_state(device_id, pause_state=is_paused)
    
    def save_device_farm_state(self, device_id: str, farm_priority: list, current_index: int):
        """Save farm state for a device"""
        self.save_device_state(
            device_id, 
            farm_priority=farm_priority,
            current_farm_index=current_index
        )
    
    def get_default_tasks(self) -> Dict[str, Any]:
        """Get default task configuration"""
        return {
            "farm": False,
            "explore": False,
            "train": False,
            "cave": False,
            "food": False,
            "wood": False,
            "stone": False,
            "gold": False,
            "built": False,
            "recruitment": False,
            "army_count": 1
        }
    
    def get_global_setting(self, key: str, default: Any = None) -> Any:
        """Get a global setting value"""
        return self.state["global_settings"].get(key, default)
    
    def set_global_setting(self, key: str, value: Any):
        """Set a global setting value"""
        self.state["global_settings"][key] = value
        self.save_state()
    
    def get_last_device(self) -> Optional[str]:
        """Get the last used device ID"""
        return self.state["global_settings"].get("last_device")
    
    def set_last_device(self, device_id: str):
        """Set the last used device ID"""
        self.state["global_settings"]["last_device"] = device_id
        self.save_state()
    
    def is_device_paused_by_default(self, device_id: str) -> bool:
        """Check if a device should start in paused state"""
        device_state = self.get_device_state(device_id)
        return device_state.get("pause_state", True)
    
    def get_all_devices(self) -> list:
        """Get list of all known devices"""
        return list(self.state["devices"].keys())
    
    def clear_device_state(self, device_id: str):
        """Clear state for a specific device"""
        if device_id in self.state["devices"]:
            del self.state["devices"][device_id]
            self.save_state()
            logger.info(f"Cleared state for device: {device_id}")
    
    def clear_all_states(self):
        """Clear all device states"""
        self.state["devices"].clear()
        self.save_state()
        logger.info("Cleared all device states")
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current state"""
        return {
            "total_devices": len(self.state["devices"]),
            "last_updated": self.state["last_updated"],
            "devices": {
                device_id: {
                    "has_tasks": bool(device_data.get("tasks")),
                    "is_paused": device_data.get("pause_state", True),
                    "last_used": device_data.get("last_used")
                }
                for device_id, device_data in self.state["devices"].items()
            }
        }
