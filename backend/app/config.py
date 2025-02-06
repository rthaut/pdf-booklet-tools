import os
from typing import List

class Settings:
    # Get environment from ENV var, default to "development"
    ENV: str = os.getenv("APP_ENV", "development")
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Get CORS origins based on environment"""
        if self.ENV == "development":
            return [
                "http://localhost:5173",  # Vite default dev server
                "http://localhost:3000",  # Alternative local port
                "http://127.0.0.1:5173",
                "http://127.0.0.1:3000",
            ]
        else:
            return [os.getenv("FRONTEND_URL")]
    
    @property
    def IS_DEVELOPMENT(self) -> bool:
        return self.ENV == "development"

# Create a settings instance
settings = Settings()
