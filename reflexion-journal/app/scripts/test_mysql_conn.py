"""
Script to test MySQL database connection using Flask-SQLAlchemy configuration.
This script reads the .env configuration and tests the database connection.
"""

import os
import sys
from datetime import datetime

# Add the project root directory to the path to allow module imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app import create_app
from app.models.models import db
from sqlalchemy import text

def test_mysql_connection():
    """Test MySQL database connection and display connection information."""
    
    try:
        app = create_app()
        
        with app.app_context():
            print("=" * 60)
            print("TESTING MySQL DATABASE CONNECTION")
            print("=" * 60)
            
            # Get database URI from configuration
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
            
            # Parse database information from URI
            if db_uri and db_uri != 'Not configured':
                # Extract info from URI (mysql://user:password@host:port/database)
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(db_uri)
                    
                    print(f"Database Configuration:")
                    print(f"   Host: {parsed.hostname}")
                    print(f"   Port: {parsed.port}")
                    print(f"   User: {parsed.username}")
                    print(f"   Database: {parsed.path[1:] if parsed.path else 'N/A'}")  # Remove leading '/'
                    print(f"   Engine: {parsed.scheme}")
                    print()
                    
                except Exception as e:
                    print(f"Could not parse database URI: {e}")
                    print(f"   Raw URI: {db_uri}")
                    print()
            
            # Test basic connection
            print("Testing database connection...")
            try:
                # Try to execute a simple query
                result = db.session.execute(text('SELECT 1 as test'))
                connection_test = result.scalar()
                
                if connection_test == 1:
                    print("Basic connection: SUCCESS")
                else:
                    print("Basic connection: FAILED")
                    return False
                    
            except Exception as e:
                print(f"Basic connection: FAILED - {str(e)}")
                return False
            
            # Test server information
            print("\nServer Information:")
            try:
                # Get MySQL version
                result = db.session.execute(text('SELECT VERSION() as version'))
                version = result.scalar()
                print(f"   MySQL Version: {version}")
                
                # Get current database
                result = db.session.execute(text('SELECT DATABASE() as current_db'))
                current_db = result.scalar()
                print(f"   Current Database: {current_db}")
                
                # Get server status
                result = db.session.execute(text('SELECT CONNECTION_ID() as connection_id'))
                connection_id = result.scalar()
                print(f"   Connection ID: {connection_id}")
                
            except Exception as e:
                print(f"Could not retrieve server info: {str(e)}")
            
            # Test table access (if tables exist)
            print("\nTable Access Test:")
            try:
                # Check if tables exist
                result = db.session.execute(text("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = DATABASE()
                """))
                tables = result.fetchall()
                
                if tables:
                    print(f"   Found {len(tables)} table(s):")
                    for table in tables:
                        print(f"     - {table[0]}")
                else:
                    print("   No tables found in database")
                    
            except Exception as e:
                print(f"Could not check tables: {str(e)}")
            
            print("\n" + "=" * 60)
            print("MySQL CONNECTION TEST COMPLETED SUCCESSFULLY")
            print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print("=" * 60)
        print("MYSQL CONNECTION TEST FAILED")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print("\nPossible solutions:")
        print("   1. Check if MySQL server is running")
        print("   2. Verify .env configuration")
        print("   3. Check database credentials")
        print("   4. Ensure database exists")
        print("   5. Check firewall/network connectivity")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_mysql_connection()
    sys.exit(0 if success else 1)