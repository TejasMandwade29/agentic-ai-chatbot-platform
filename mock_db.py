import json

# In-memory mock database of transactions
# Simulates a real database for demonstration purposes.
TRANSACTIONS = {
    "TXN-1001": {
        "user_id": "USR-555",
        "amount": 49.99,
        "currency": "USD",
        "status": "Success",
        "date": "2026-08-01",
        "description": "Pro Plan Subscription",
        "duplicate_count": 1
    },
    "TXN-1002": {
        "user_id": "USR-777",
        "amount": 99.00,
        "currency": "USD",
        "status": "Success",
        "date": "2026-08-02",
        "description": "Annual Premium Subscription",
        "duplicate_count": 2  # Flagged as a duplicate charge
    },
    "TXN-1003": {
        "user_id": "USR-999",
        "amount": 15.00,
        "currency": "USD",
        "status": "Failed",
        "date": "2026-08-02",
        "description": "One-time purchase",
        "duplicate_count": 1
    }
}

def get_transaction(transaction_id: str) -> dict:
    """Simulates a DB lookup for a transaction."""
    return TRANSACTIONS.get(transaction_id, {"error": "Transaction not found"})

def update_transaction_status(transaction_id: str, new_status: str) -> dict:
    """Simulates updating a transaction status in the DB."""
    if transaction_id in TRANSACTIONS:
        TRANSACTIONS[transaction_id]["status"] = new_status
        return {"success": True, "transaction": TRANSACTIONS[transaction_id]}
    return {"error": "Transaction not found"}
