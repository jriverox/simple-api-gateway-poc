import yaml
from pathlib import Path
#from functools import lru_cache
from .models import Settings

#@lru_cache
def get_settings(settings_path: str = "settings.yaml") -> Settings:
    yaml_path = Path(settings_path)
    if not yaml_path.exists():
        raise FileNotFoundError(f"Settings file not found: {settings_path}")
    
    with open(yaml_path) as f:
        settings_dict = yaml.safe_load(f)
    
    return Settings(**settings_dict)