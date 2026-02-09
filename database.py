from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

db = SQLAlchemy()
migrate = Migrate()

def get_model_fields(model):
    """Возвращает список полей модели SQLAlchemy"""
    inspector = inspect(model)
    fields = []
    for column in inspector.mapper.columns:
        fields.append({
            'name': column.name,
            'type': str(column.type),
            'nullable': column.nullable,
            'primary_key': column.primary_key,
            'foreign_key': column.foreign_keys
        })
    return fields

def get_tables_name():
    return inspect(db.engine).get_table_names()
