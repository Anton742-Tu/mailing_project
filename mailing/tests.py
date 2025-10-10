from django.db import connection
from django.test import TestCase


class DatabaseTest(TestCase):
    def test_database_connection(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"PostgreSQL version: {version[0]}")
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Database connection failed: {e}")
