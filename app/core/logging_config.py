import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional
import structlog
from app.core.config import settings
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)

def get_correlation_id() -> str:
    cid = correlation_id_var.get()
    if cid is None:
        cid = str(uuid.uuid4())
        correlation_id_var.set(cid)
    return cid

def set_correlation_id(cid: str) -> None:
    correlation_id_var.set(cid)

def add_correlation_id(logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    event_dict['correlation_id'] = get_correlation_id()
    return event_dict

def add_service_info(logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    event_dict['service'] = getattr(settings, "APP_NAME", "OMNIA")
    event_dict['version'] = getattr(settings, "APP_VERSION", "1.0.0")
    event_dict['environment'] = getattr(settings, "ENVIRONMENT", "development")
    return event_dict

def setup_logging() -> None:
    # Defensive access (prevents CI crashes)
    log_level_name = getattr(settings, "LOG_LEVEL", "INFO")
    log_format = getattr(settings, "LOG_FORMAT", "console")

    log_level = getattr(logging, log_level_name.upper(), logging.INFO)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        add_correlation_id,
        add_service_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if log_format == "json":
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if getattr(settings, "DATABASE_ECHO", False) else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("aiokafka").setLevel(logging.WARNING)

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)

class LoggerAdapter:

    def __init__(self, name: str):
        self._logger = get_logger(name)

    def debug(self, msg: str, *args, **kwargs) -> None:
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self._logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        self._logger.exception(msg, *args, **kwargs)