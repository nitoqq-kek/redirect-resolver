import logging.config


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"verbose": {"format": "%(asctime)s %(name)s %(levelname)s: %(message)s"}},
    "handlers": {"console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "verbose"}},
    "loggers": {"": {"handlers": ["console"], "level": logging.INFO}},
}


def init_logging(level=logging.DEBUG):
    LOGGING["loggers"].update({**LOGGING["loggers"], "": {"handlers": ["console"], "level": level}})
    logging.config.dictConfig(LOGGING)
