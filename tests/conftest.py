import pytest
import os
import importlib
from app import create_app
from app.infrastructure.database import db

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def import_all_models():
    models_dir = os.path.join(os.path.dirname(__file__), '../app/domain/models')
    for filename in os.listdir(models_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = f"app.domain.models.{filename[:-3]}"
            importlib.import_module(module_name)

@pytest.fixture(autouse=True)
def app_context():
    app = create_app(TestConfig)
    with app.app_context():
        import_all_models()
        db.create_all()
        yield app
        db.drop_all()

