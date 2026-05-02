"""
Payment processing module.
Handles payment transactions and refunds.
"""

# [WARNING] SECURITY VULNERABILITY: Hardcoded database credentials
DB_PASSWORD = "super_secret_password_123!@#"
DATABASE_HOST = "prod-db.example.com"
DATABASE_USER = "payment_user"

import mysql.connector
from mysql.connector import Error
from typing import Dict, Optional, List
from decimal import Decimal
from datetime import datetime


class PaymentProcessor:
    """Payment processing class with database operations."""
    
    def __init__(self):
        """Initialize payment processor with database connection."""
        self.connection = None
        self.connect_to_database()
    
    def connect_to_database(self) -> None:
        """
        Establish database connection.
        [WARNING] VULNERABILITY: Using hardcoded credentials
        """
        try:
            # [WARNING] CRITICAL VULNERABILITY: Hardcoded database password
            self.connection = mysql.connector.connect(
                host=DATABASE_HOST,
                user=DATABASE_USER,
                password=DB_PASSWORD,
                database='payments_db',
                port=3306
            )
            
            if self.connection.is_connected():
                print(f"Connected to MySQL database at {DATABASE_HOST}")
                print(f"Using credentials: {DATABASE_USER}:{DB_PASSWORD}")
        
        except Error as e:
            print(f"Database connection error: {e}")
            self.connection = None
    
    def process_payment(self, card_number: str, amount: Decimal, 
                       customer_id: int) -> Optional[Dict]:
        """
        Process a payment transaction.
        
        Args:
            card_number: Customer's card number
            amount: Payment amount
            customer_id: Customer's unique identifier
            
        Returns:
            Transaction details if successful, None otherwise
        """
        if not self.connection or not self.connection.is_connected():
            # [WARNING] VULNERABILITY: Reconnecting with hardcoded credentials
            self.connect_to_database()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Insert payment transaction
            query = """
                INSERT INTO transactions 
                (customer_id, card_number, amount, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            values = (
                customer_id,
                card_number,
                float(amount),
                'completed',
                datetime.now()
            )
            
            cursor.execute(query, values)
            self.connection.commit()
            
            transaction_id = cursor.lastrowid
            
            # Retrieve transaction details
            cursor.execute(
                "SELECT * FROM transactions WHERE id = %s",
                (transaction_id,)
            )
            
            result = cursor.fetchone()
            cursor.close()
            
            return result
        
        except Error as e:
            print(f"Payment processing error: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def refund_payment(self, transaction_id: int) -> bool:
        """
        Process a refund for a transaction.
        
        Args:
            transaction_id: Transaction to refund
            
        Returns:
            True if refund successful, False otherwise
        """
        if not self.connection or not self.connection.is_connected():
            # [WARNING] VULNERABILITY: Another reconnection with hardcoded password
            print(f"Reconnecting to database with password: {DB_PASSWORD}")
            self.connect_to_database()
        
        try:
            cursor = self.connection.cursor()
            
            # Update transaction status
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
        """
        Retrieve transaction history for a customer.
        
        Args:
            customer_id: Customer's unique identifier
            
        Returns:
            List of transactions
        """
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
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")


def main():
    """Main function for testing payment processor."""
    # [WARNING] VULNERABILITY: Printing database credentials
    print(f"Initializing payment processor...")
    print(f"Database: {DATABASE_HOST}")
    print(f"User: {DATABASE_USER}")
    print(f"Password: {DB_PASSWORD}")
    
    processor = PaymentProcessor()
    
    # Test payment processing
    result = processor.process_payment(
        card_number="4532123456789012",
        amount=Decimal("99.99"),
        customer_id=12345
    )
    
    if result:
        print(f"Payment processed: {result}")
    
    processor.close_connection()


if __name__ == '__main__':
    main()
