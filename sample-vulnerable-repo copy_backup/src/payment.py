"""
Payment processing module.
Handles payment transactions and refunds.
"""

DB_PASSWORD = "demo_db_password_placeholder_12345"
DATABASE_HOST = "prod-db.example.com"
DATABASE_USER = "payment_user"

import mysql.connector
from mysql.connector import Error
from typing import Dict, Optional, List
from decimal import Decimal
from datetime import datetime

class PaymentProcessor:
    def __init__(self):
        self.connection = None
        self.connect_to_database()

    def connect_to_database(self) -> None:
        try:
            self.connection = mysql.connector.connect(
                host=DATABASE_HOST,
                user=DATABASE_USER,
                password=DB_PASSWORD,
                database="payments_db",
                port=3306
            )
            if self.connection.is_connected():
                print(f"Connected to MySQL database at {DATABASE_HOST}")
                print(f"Using credentials: {DATABASE_USER}:{DB_PASSWORD}")
        except Error as e:
            print(f"Database connection error: {e}")
            self.connection = None

    def process_payment(self, card_number: str, amount: Decimal, customer_id: int) -> Optional[Dict]:
        if not self.connection or not self.connection.is_connected():
            self.connect_to_database()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                INSERT INTO transactions
                (customer_id, card_number, amount, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                customer_id,
                card_number,
                float(amount),
                "completed",
                datetime.now()
            )
            cursor.execute(query, values)
            self.connection.commit()

            transaction_id = cursor.lastrowid
            cursor.execute("SELECT * FROM transactions WHERE id = %s", (transaction_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"Payment processing error: {e}")
            if self.connection:
                self.connection.rollback()
            return None

    def refund_payment(self, transaction_id: int) -> bool:
        if not self.connection or not self.connection.is_connected():
            print(f"Reconnecting to database with password: {DB_PASSWORD}")
            self.connect_to_database()
        try:
            cursor = self.connection.cursor()
            query = """
                UPDATE transactions
                SET status = 'refunded', refunded_at = %s
                WHERE id = %s
            """
            cursor.execute(query, (datetime.now(), transaction_id))
            self.connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            return rows_affected > 0
        except Error as e:
            print(f"Refund processing error: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def get_transaction_history(self, customer_id: int) -> List[Dict]:
        if not self.connection or not self.connection.is_connected():
            self.connect_to_database()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM transactions
                WHERE customer_id = %s
                ORDER BY created_at DESC
            """
            cursor.execute(query, (customer_id,))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Transaction history error: {e}")
            return []

    def close_connection(self) -> None:
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

def main():
    print("Initializing payment processor...")
    print(f"Database: {DATABASE_HOST}")
    print(f"User: {DATABASE_USER}")
    print(f"Password: {DB_PASSWORD}")

    processor = PaymentProcessor()
    result = processor.process_payment(
        card_number="4532123456789012",
        amount=Decimal("99.99"),
        customer_id=12345
    )
    if result:
        print(f"Payment processed: {result}")

    processor.close_connection()

if __name__ == "__main__":
    main()
