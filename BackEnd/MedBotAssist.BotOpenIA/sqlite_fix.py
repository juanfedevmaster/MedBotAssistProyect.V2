"""
SQLite3 compatibility fix for ChromaDB in Azure App Service
"""
import sys

# Force use of pysqlite3 instead of system sqlite3
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
