"""
Source Manager Application Package
Sets up clean imports for all modules
"""
import sys
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import and expose all submodules
from . import controllers
from . import models
from . import services
from . import views

# Also expose the classes directly for clean imports
from .controllers import *
from .models import *
from .services import *
from .views import *