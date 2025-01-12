import re
from datetime import datetime
from typing import Dict, Optional

class MPESAMessageParser:
    def __init__(self):
        # Main regex pattern to match different transaction types
        pattern_str = (
            # Transaction ID
            r"(?P<transaction_id>[A-Z0-9]{10})\s+"
            r"[Cc]onfirmed\.?\s*"
            
            # Main transaction patterns
            r"(?:"
            # Pattern for receiving money
            r"(?:You\shave\sreceived\sKsh(?P<received_amount>[\d,.]+)\sfrom\s(?P<sender_name>[^0-9]+?)(?:\s(?P<sender_phone>\d+))?)|"
            
            # Pattern for payments to till/paybill/merchant
            r"(?:Ksh(?P<paid_amount>[\d,.]+)\spaid\sto\s(?P<paid_to>[^.]+))|"
            
            # Pattern for sending money (including to bank accounts)
            r"(?:Ksh(?P<sent_amount>[\d,.]+)\ssent\sto\s(?P<recipient>[^0-9]+?)(?:\sfor\saccount\s(?P<account_number>[^\s]+))?(?:\s(?P<recipient_phone>\d+))?)|"
            
            # Pattern for M-Shwari transfers
            r"(?:Ksh(?P<mshwari_amount>[\d,.]+)\stransferred\s(?P<mshwari_direction>(?:from|to))\sM-Shwari\saccount)|"
            
            # Pattern for airtime purchase
            r"(?:You\sbought\sKsh(?P<airtime_amount>[\d,.]+)\sof\sairtime(?:\sfor\s(?P<airtime_phone>\d+))?)|"
            
            # Pattern for withdrawal - Updated to be more flexible with spacing
            r"(?:(?:on\s[^.]+?)?\s*Withdraw\s*Ksh(?P<withdraw_amount>[\d,.]+)\sfrom\s(?P<agent_details>[^.]+))|"
            
            # Pattern for balance check
            r"(?:Your\saccount\sbalance\swas:\sM-PESA\sAccount\s:\sKsh(?P<balance_amount>[\d,.]+))"
            r")"
            
            # Date and time - Made more flexible with optional spaces
            r".*?(?:on\s)?(?P<date>\d{1,2}/\d{1,2}/\d{2})\sat\s(?P<time>\d{1,2}:\d{2}\s*[AP]M)"
            
            # Balance(s)
            r"(?:.*?(?:New\s)?(?:M-PESA\s)?balance(?:\sis)?\sKsh(?P<mpesa_balance>[\d,.]+))"
            r"(?:.*?M-Shwari\s(?:balance|saving\saccount\sbalance)(?:\sis)?\sKsh(?P<mshwari_balance>[\d,.]+))?"
            
            # Transaction cost
            r"(?:.*?Transaction\scost(?:\s|,\s)?Ksh(?P<transaction_cost>\.?\d+\.?\d*)?)?"
            
            # Daily transaction limit
            r"(?:.*?Amount\syou\scan\stransact\swithin\sthe\sday\sis\s(?P<daily_limit>[\d,.]+))?"
        )
        
        self.pattern = re.compile(pattern_str)
        
        # Pattern for failed transactions
        self.failed_pattern = re.compile(
            r"Failed\.\s"
            r"(?:"
            r"(?:You\sdo\snot\shave\senough\smoney)|"
            r"(?:Insufficient\sfunds\sin\syour\sM-PESA\saccount)|"
            r"(?:You\shave\sinsufficient\sfunds)|"
            r"(?:Insufficient\sfunds\sin\syour\sM-PESA\saccount\sas\swell\sas\sFuliza\sM-PESA)|"
            r"(?:You\shave\sinsufficient\sfunds\sin\syour\sM-Shwari\saccount)"
            r")"
        )

    # Rest of the class implementation remains the same
    def clean_amount(self, amount_str: str) -> float:
        """Clean amount string and convert to float."""
        # Remove commas
        cleaned = amount_str.replace(',', '')
        
        # Handle case where amount starts with decimal point
        if cleaned.startswith('.'):
            cleaned = '0' + cleaned
            
        # Remove any trailing periods or spaces
        cleaned = cleaned.strip().rstrip('.')
        
        # Handle possible double decimals (like .0.00)
        if cleaned.count('.') > 1:
            parts = cleaned.split('.')
            cleaned = parts[0] + '.' + parts[-1]
            
        return float(cleaned)
        
    def parse_message(self, message: str) -> Dict[str, any]:
        """Parse an M-PESA message and extract relevant details."""
        if not isinstance(message, str):
            return {"error": "Input must be a string"}
            
        # Check if this is a failed transaction
        failed_match = self.failed_pattern.search(message)
        
        match = self.pattern.search(message)
        if not match:
            return {"error": "Message format not recognized"}
            
        result = {k: v for k, v in match.groupdict().items() if v is not None}
        
        # Clean up values - remove trailing spaces
        for key in result:
            if isinstance(result[key], str):
                result[key] = result[key].strip()
        
        # Set transaction status
        result['status'] = 'FAILED' if failed_match else 'SUCCESS'
        
        # Determine transaction type
        if result.get('received_amount'):
            result['transaction_type'] = 'RECEIVED'
            result['amount'] = result.pop('received_amount')
        elif result.get('paid_amount'):
            result['transaction_type'] = 'PAID'
            result['amount'] = result.pop('paid_amount')
        elif result.get('sent_amount'):
            result['transaction_type'] = 'SENT'
            result['amount'] = result.pop('sent_amount')
        elif result.get('mshwari_amount'):
            if result.get('mshwari_direction') == 'from':
                result['transaction_type'] = 'MSHWARI_WITHDRAWAL'
            else:
                result['transaction_type'] = 'MSHWARI_DEPOSIT'
            result['amount'] = result.pop('mshwari_amount')
        elif result.get('airtime_amount'):
            result['transaction_type'] = 'AIRTIME'
            result['amount'] = result.pop('airtime_amount')
        elif result.get('withdraw_amount'):
            result['transaction_type'] = 'WITHDRAW'
            result['amount'] = result.pop('withdraw_amount')
        elif result.get('balance_amount'):
            result['transaction_type'] = 'BALANCE_CHECK'
            result['amount'] = result.pop('balance_amount')
            
        # Convert numeric values to float using the clean_amount method
        for key in ['amount', 'mpesa_balance', 'mshwari_balance', 'transaction_cost', 'daily_limit']:
            if key in result:
                try:
                    result[key] = self.clean_amount(result[key])
                except (ValueError, AttributeError) as e:
                    print(f"Error converting {key}: {result[key]}")
                    raise
                
        # Parse date and time
        if 'date' in result and 'time' in result:
            datetime_str = f"{result['date']} {result['time']}"
            result['datetime'] = datetime.strptime(datetime_str, '%d/%m/%y %I:%M %p')
            
        return result

# def test_parser():
#     parser = MPESAMessageParser()
    
#     # Read messages from file
#     with open('messages.txt', 'r') as f:
#         messages = f.readlines()
    
#     for message in messages:
#         if message.strip():  # Skip empty lines
#             print("\nOriginal Message:", message.strip())
#             try:
#                 result = parser.parse_message(message)
#                 print("Parsed Result:")
#                 for key, value in result.items():
#                     print(f"{key}: {value}")
#             except Exception as e:
#                 print(f"Error parsing message: {str(e)}")

def test_parser_with_user_input():
    parser = MPESAMessageParser()
    
    print("Welcome to the M-PESA Message Parser!")
    print("Enter your M-PESA message below (type 'exit' to quit):\n")
    
    while True:
        # Prompt the user for input
        message = input("Enter M-PESA message: ").strip()
        
        if message.lower() == 'exit':  # Exit condition
            print("Exiting the parser. Goodbye!")
            break
        
        if message:  # Only process non-empty messages
            print("\nOriginal Message:", message)
            try:
                result = parser.parse_message(message)
                print("Parsed Result:")
                for key, value in result.items():
                    print(f"{key}: {value}")
            except Exception as e:
                print(f"Error parsing message: {str(e)}")
        else:
            print("No input detected. Please enter a valid M-PESA message or type 'exit' to quit.\n")


if __name__ == "__main__":
    # test_parser()
    test_parser_with_user_input()
    
