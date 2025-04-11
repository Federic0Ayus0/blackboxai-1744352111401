import os
import logging

# Database Configuration
DATABASE_NAME = 'invoice_system.db'

# Logging Configuration
LOG_FILE = 'app.log'
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=LOG_LEVEL,
    format=LOG_FORMAT
)

logger = logging.getLogger(__name__)
