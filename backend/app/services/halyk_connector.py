import os
import uuid

class HalykConnector:
    """
    Mock Halyk Bank OpenBanking Integration
    Provides checking accounts, balance, and mock payment gateway.
    """
    def __init__(self):
        self.mock = os.getenv("EGOV_MOCK", "true").lower() == "true"
        # Seed mock bank data per iin
        self._accounts = {
            "870412300415": [
                {"account_id": "KZ1234567890", "type": "debit", "balance": 450000.0, "currency": "KZT"}
            ]
        }

    def get_accounts(self, iin: str) -> list:
        if not self.mock:
            raise Exception("Halyk prod bank integration not configured")
        if iin not in self._accounts:
            self._accounts[iin] = [
                {
                    "account_id": f"KZ{iin[-6:]}{'0' * 4}",
                    "type": "debit",
                    "balance": 250_000.0,
                    "currency": "KZT",
                }
            ]
        return self._accounts[iin]

    def process_payment(self, iin: str, amount: float, purpose: str) -> dict:
        accounts = self.get_accounts(iin)
        if not accounts:
            return {"success": False, "error": "No accounts found for IIN"}
        
        main_account = accounts[0]
        if main_account["balance"] < amount:
            return {"success": False, "error": "Insufficient funds"}
            
        main_account["balance"] -= amount
        return {
            "success": True, 
            "transaction_id": str(uuid.uuid4()),
            "old_balance": main_account["balance"] + amount,
            "new_balance": main_account["balance"],
            "purpose": purpose
        }

halyk_bank = HalykConnector()
