
from fastapi import APIRouter,status

test_router = APIRouter(prefix="/test",tags=["Test"])

@test_router.get("/",status_code=status.HTTP_201_CREATED)
async def test_endpoint():
    return {"message": "Test endpoint is working!"}