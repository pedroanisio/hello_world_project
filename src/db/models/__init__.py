from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta

# Create the declarative base
Base: DeclarativeMeta = declarative_base()

# Import all models here to ensure they are registered with SQLAlchemy
from .user import User  # noqa: F401
from .example_model import ExampleModel  # noqa: F401