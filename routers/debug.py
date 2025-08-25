from fastapi import APIRouter
import logging

router = APIRouter(prefix="/debug", tags=["Debug"])

@router.get("/log_test")
async def log_test():
    logging.info("This is a test log message from the /debug/log_test endpoint.")
    return {"message": "Log test message sent. Please check your log file."}
