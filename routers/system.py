from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
import platform
import psutil
import os
from config import settings

router = APIRouter(prefix="/system", tags=["System"])

class HealthResponse(BaseModel):
    status: str
    version: str
    
class SystemInfoResponse(BaseModel):
    status: str
    version: str
    python_version: str
    os_info: str
    cpu_usage: float
    memory_usage: Dict[str, Any]
    storage_info: Dict[str, Any]
    config: Dict[str, Any]

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System health check",
    description="Check the health status of the API",
    response_description="Health status information",
)
async def health_check():
    """
    Check the health status of the API.
    """
    return {"status": "healthy", "version": "0.2.0"}

@router.get(
    "/info",
    response_model=SystemInfoResponse,
    summary="System information",
    description="Get detailed information about the system",
    response_description="Detailed system information",
)
async def system_info():
    """
    Get detailed information about the system, including resource usage and configuration.
    """
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Filter sensitive information from settings
    safe_settings = {
        "chroma_db_path": settings.chroma_db_path,
        "log_path": settings.log_path,
        "crawler_depth": settings.crawler_depth,
        "crawler_max_pages": settings.crawler_max_pages,
        "document_store_path": settings.document_store_path
    }
    
    return {
        "status": "healthy",
        "version": "0.2.0",
        "python_version": platform.python_version(),
        "os_info": f"{platform.system()} {platform.release()}",
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": {
            "total": f"{memory.total / (1024**3):.2f} GB",
            "available": f"{memory.available / (1024**3):.2f} GB",
            "percent": memory.percent
        },
        "storage_info": {
            "total": f"{disk.total / (1024**3):.2f} GB",
            "used": f"{disk.used / (1024**3):.2f} GB",
            "free": f"{disk.free / (1024**3):.2f} GB",
            "percent": disk.percent
        },
        "config": safe_settings
    }