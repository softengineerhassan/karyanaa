from contextlib import asynccontextmanager
import time
from datetime import timedelta

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging_config import get_logger, setup_logging
from app.database.session import close_db, init_db
from app.core.middlewares import (
    CorrelationIdMiddleware,
    MetricsMiddleware,
    metrics_tracker
)
from app.api import api_router
from app.utils.exceptions import AuthServiceException

# Tracking startup time
from app.core.startup import START_TIME

# Setup logging
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting OMNIA')
    try:
        # logger.info('Initializing database connection...')
        # init_db()
        # logger.info('Database connection established')
        if settings.ENVIRONMENT != "test":
            logger.info('Initializing database connection...')
            init_db()
            logger.info('Database connection established')
        else:
            logger.info("Skipping database init in test environment")
        
        # Redis disabled - uncomment to enable caching
        # try:
        #     from app.cache.redis_client import redis_client
        #     await redis_client.connect()
        #     logger.info('Redis connection established')
        # except Exception as e:
        #     logger.warning(f'Redis connection failed: {e}. Continuing without cache.')
        
        logger.info(
            f'Auth-Service started successfully',
            extra={
                'environment': settings.ENVIRONMENT,
                'debug': settings.DEBUG,
                'kafka_enabled': settings.KAFKA_ENABLED
            }
        )
        yield
    finally:
        logger.info('Shutting down OMNIA')
        
        # Redis disabled - uncomment to enable caching
        # try:
        #     from app.cache.redis_client import redis_client
        #     await redis_client.disconnect()
        #     logger.info('Redis connection closed')
        # except Exception as e:
        #     logger.warning(f'Error closing Redis: {e}')
        
        close_db()
        logger.info('Database connection closed')
        logger.info('Auth-Service shutdown complete')


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="KARYANAA",
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
    lifespan=lifespan,
)


# CORS middleware (must be first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS
)

# Correlation ID middleware
app.add_middleware(CorrelationIdMiddleware)

# Metrics middleware (must be after CorrelationId to track full request)
app.add_middleware(MetricsMiddleware)


# Note: Rate limiting middleware is applied per-endpoint using dependencies
# to allow for granular control

# ============================================
# Exception Handlers
# ============================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Filter out 'Expected UploadFile' errors for image_gallery from Swagger empty strings."""
    real_errors = []
    for error in exc.errors():
        loc = error.get("loc", [])
        parent_field = loc[1] if len(loc) > 1 else ""
        if parent_field == "image_gallery" and "Expected UploadFile" in str(error.get("msg", "")):
            continue
        real_errors.append(error)
    
    if real_errors:
        return JSONResponse(status_code=422, content={"detail": real_errors})
    
    # Only image_gallery empty-string errors — return standard 422 with helpful message
    return JSONResponse(status_code=422, content={
        "detail": "Please uncheck 'Send empty value' for image_gallery if you don't want to upload gallery images, or select actual files."
    })

@app.exception_handler(AuthServiceException)
async def auth_service_exception_handler(request: Request, exc: AuthServiceException):
    logger.warning(
        f"Auth exception: {exc.message}",
        extra={
            "path": request.url.path,
            "status_code": exc.status_code,
            "details": exc.details
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={"path": request.url.path},
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "details": {"error": str(exc)} if settings.DEBUG else {}
        }
    )

app.include_router(api_router, prefix="/api/v1")



@app.get('/health', tags=['Health'])
async def health_check():
    start_ts = time.perf_counter()
    uptime_seconds = time.time() - START_TIME
    
    # Format uptime
    uptime_str = str(timedelta(seconds=int(uptime_seconds)))
    
    # Get global average response time
    avg_response_time = metrics_tracker.get_average()
    
    # Current request execution time
    current_execution_time_ms = (time.perf_counter() - start_ts) * 1000
    
    return {
        'status': 'healthy', 
        'service': settings.APP_NAME, 
        'version': settings.APP_VERSION,
        'uptime': uptime_str,
        'average_response_time_ms': round(avg_response_time, 4),
        'health_check_execution_time_ms': round(current_execution_time_ms, 4)
    }


@app.get('/health/ready', tags=['Health'])
async def readiness_check():
    health_status = {'status': 'ready', 'checks': {}}
    all_healthy = True
    
    try:
        from app.database.session import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        health_status['checks']['database'] = {'status': 'healthy'}
    except Exception as e:
        health_status['checks']['database'] = {'status': 'unhealthy', 'error': str(e)}
        all_healthy = False
    
    # Redis disabled - uncomment to enable caching
    # try:
    #     from app.cache.redis_client import redis_client
    #     if await redis_client.ping():
    #         health_status['checks']['redis'] = {'status': 'healthy'}
    #     else:
    #         health_status['checks']['redis'] = {'status': 'unhealthy'}
    # except Exception as e:
    #     health_status['checks']['redis'] = {'status': 'unavailable', 'error': str(e)}
    
    if not all_healthy:
        health_status['status'] = 'degraded'
    return health_status

@app.get('/health/live', tags=['Health'])
async def liveness_check():
    return {'status': 'alive'}


@app.get('/', tags=['Root'])
async def root():
    return {'service': settings.APP_NAME, 'version': settings.APP_VERSION, 'environment': settings.ENVIRONMENT, 'docs': '/docs' if settings.DEBUG else 'Disabled in production'}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
