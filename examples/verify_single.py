"""
Example: Verify a single email address
"""

from emaillistchecker import EmailListChecker, EmailListCheckerException

# Initialize the client with your API key
client = EmailListChecker(api_key='your_api_key_here')

try:
    # Verify an email address
    result = client.verify('test@example.com')

    print("Verification Result:")
    print(f"Email: {result['email']}")
    print(f"Result: {result['result']}")
    print(f"Reason: {result['reason']}")
    print(f"Score: {result['score']}")
    print(f"Disposable: {result['disposable']}")
    print(f"Role Account: {result['role']}")
    print(f"Free Provider: {result['free']}")
    print(f"SMTP Provider: {result['smtp_provider']}")

    # Check if email is deliverable
    if result['result'] == 'deliverable':
        print("\n✓ Email is valid and deliverable!")
    elif result['result'] == 'undeliverable':
        print("\n✗ Email is invalid or undeliverable")
    elif result['result'] == 'risky':
        print("\n⚠ Email is risky (catch-all, disposable, etc.)")
    else:
        print("\n? Unable to determine deliverability")

except EmailListCheckerException as e:
    print(f"Error: {e.message}")
