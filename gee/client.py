"""
Google Earth Engine authentication and client management
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path


class GEEClient:
    """
    Google Earth Engine client with smart authentication chain
    """
    
    def __init__(self, service_account_path: Optional[str] = None):
        """
        Initialize GEE client with authentication
        
        Args:
            service_account_path: Path to service account JSON file
        """
        self.service_account_path = service_account_path
        self.authenticated = False
        self._ee = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
    
    def authenticate(self) -> bool:
        """
        Smart authentication chain: service account → user auth → fallback
        
        Returns:
            bool: True if authentication successful
        """
        try:
            import ee
            self._ee = ee
        except ImportError:
            self.logger.error("❌ Google Earth Engine Python API not installed")
            self.logger.info("💡 Install with: pip install earthengine-api")
            return False
        
        # Try service account authentication first
        if self._try_service_account_auth():
            return True
        
        # Try user authentication
        if self._try_user_auth():
            return True
        
        # Fallback: interactive authentication
        return self._try_interactive_auth()
    
    def _try_service_account_auth(self) -> bool:
        """Try service account authentication"""
        if not self.service_account_path:
            self.logger.info("🔍 No service account path provided, skipping...")
            return False
        
        service_path = Path(self.service_account_path)
        if not service_path.exists():
            self.logger.warning(f"🔍 Service account file not found: {service_path}")
            return False
        
        try:
            credentials = self._ee.ServiceAccountCredentials(
                email=None,  # Will be read from JSON
                key_file=str(service_path)
            )
            self._ee.Initialize(credentials)
            self.logger.info("✅ Service account authentication successful")
            self.authenticated = True
            return True
        except Exception as e:
            self.logger.warning(f"⚠️ Service account auth failed: {e}")
            return False
    
    def _try_user_auth(self) -> bool:
        """Try existing user authentication"""
        try:
            self._ee.Initialize()
            # Test with a simple operation
            self._ee.Image("MODIS/006/MOD10A1").limit(1).getInfo()
            self.logger.info("✅ Existing user authentication successful")
            self.authenticated = True
            return True
        except Exception as e:
            self.logger.info(f"🔍 User auth not available: {e}")
            return False
    
    def _try_interactive_auth(self) -> bool:
        """Try interactive authentication"""
        try:
            self.logger.info("🔐 Starting interactive authentication...")
            self.logger.info("📱 This will open a browser for Google authentication")
            
            self._ee.Authenticate()
            self._ee.Initialize()
            
            self.logger.info("✅ Interactive authentication successful")
            self.authenticated = True
            return True
        except Exception as e:
            self.logger.error(f"❌ Interactive authentication failed: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.authenticated
    
    def get_ee(self):
        """Get the Earth Engine module (requires authentication)"""
        if not self.authenticated:
            raise RuntimeError("GEE client not authenticated. Call authenticate() first.")
        return self._ee
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test GEE connection and return system info
        
        Returns:
            Dict with connection test results
        """
        if not self.authenticated:
            return {"status": "error", "message": "Not authenticated"}
        
        try:
            # Simple test: get MODIS collection info
            collection = self._ee.ImageCollection("MODIS/006/MCD43A3")
            size = collection.size()
            
            result = {
                "status": "success",
                "message": "GEE connection successful",
                "test_collection": "MODIS/006/MCD43A3",
                "collection_size": size.getInfo(),
                "authenticated": True
            }
            
            self.logger.info("✅ GEE connection test successful")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ GEE connection test failed: {e}")
            return {
                "status": "error", 
                "message": f"Connection test failed: {e}",
                "authenticated": self.authenticated
            }
    
    @staticmethod
    def check_installation() -> Dict[str, Any]:
        """
        Check if Earth Engine is properly installed
        
        Returns:
            Dict with installation status
        """
        try:
            import ee
            return {
                "installed": True,
                "version": getattr(ee, "__version__", "unknown"),
                "module_path": ee.__file__
            }
        except ImportError:
            return {
                "installed": False,
                "install_command": "pip install earthengine-api"
            }