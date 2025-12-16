# create_tables.py
from db import engine, Base
import api.models  # ensure model imported so metadata is registered

Base.metadata.create_all(bind=engine)
print("Tables created (if not existed).")
