---

# M-PESA Message Parser

This Python program parses M-PESA transaction messages to extract relevant details such as transaction type, amount, sender/recipient details, and balances. It supports both single message input (via user interaction) and batch processing of multiple messages stored in a file.

---

## **How to Use**

### **1. Single Message Input (Default Mode)**
This mode allows you to input one M-PESA message at a time interactively.

- Run the script:
  ```bash
  python your_script_name.py
  ```
- You will be prompted to enter an M-PESA message. Type or paste the message and press Enter.
- The program will parse the message and display the extracted details.
- To exit, type `exit`.

---

### **2. Batch Processing of Multiple Messages**
If you want to parse multiple messages at once, store them in a file named `messages.txt` (one message per line) and enable batch processing.

- Update the code:
  - **Uncomment** the batch processing function:
    ```python
    def test_parser():
        parser = MPESAMessageParser()
        
        # Read messages from file
        with open('messages.txt', 'r') as f:
            messages = f.readlines()
        
        for message in messages:
            if message.strip():  # Skip empty lines
                print("\nOriginal Message:", message.strip())
                try:
                    result = parser.parse_message(message)
                    print("Parsed Result:")
                    for key, value in result.items():
                        print(f"{key}: {value}")
                except Exception as e:
                    print(f"Error parsing message: {str(e)}")
    ```
  - **Comment out** the single-message input function:
    ```python
    # def test_parser_with_user_input():
    #     parser = MPESAMessageParser()
    #     print("Welcome to the M-PESA Message Parser!")
    #     print("Enter your M-PESA message below (type 'exit' to quit):\n")
    #     while True:
    #         message = input("Enter M-PESA message: ").strip()
    #         if message.lower() == 'exit':
    #             print("Exiting the parser. Goodbye!")
    #             break
    #         if message:
    #             print("\nOriginal Message:", message)
    #             try:
    #                 result = parser.parse_message(message)
    #                 print("Parsed Result:")
    #                 for key, value in result.items():
    #                     print(f"{key}: {value}")
    #             except Exception as e:
    #                 print(f"Error parsing message: {str(e)}")
    #         else:
    #             print("No input detected. Please enter a valid M-PESA message or type 'exit' to quit.\n")
    ```

- Create a `messages.txt` file and add one M-PESA message per line.
- Run the script:
  ```bash
  python your_script_name.py
  ```

The program will parse all messages in `messages.txt` and display the results.

---

## **Requirements**
- Python 3.6+
- No external dependencies are required.

---

## **Features**
- Supports a wide range of M-PESA transaction types:
  - Money received
  - Payments to merchants or paybills
  - Sending money
  - Airtime purchases
  - Withdrawals
  - Balance checks
- Detects failed transactions.
- Converts monetary values to clean, float numbers.
- Parses date and time into Python `datetime` objects.

---

## **Contributing**
Feel free to submit issues or pull requests if you have suggestions for improving this parser!

---

## **License**
This project is licensed under the MIT License.

---
