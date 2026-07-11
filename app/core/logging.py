import logging
import sys
import structlog


def setup_logging():
    """
    Configure application logging.
    """

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )


    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,

            structlog.processors.add_log_level,

            structlog.processors.TimeStamper(
                fmt="iso"
            ),

            structlog.processors.JSONRenderer(),
        ],

        wrapper_class=structlog.make_filtering_bound_logger(
            logging.INFO
        ),

        logger_factory=structlog.PrintLoggerFactory(),

    )


def get_logger(name: str):
    """
    Returns structured logger.
    """

    return structlog.get_logger(name)