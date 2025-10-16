"""
Example: Batch email verification
"""

import time
from emaillistchecker import EmailListChecker

client = EmailListChecker(api_key='your_api_key_here')

# List of emails to verify
emails = [
    'user1@example.com',
    'user2@example.com',
    'user3@example.com',
    'invalid@invalid-domain-xyz.com'
]

# Submit batch for verification
print("Submitting batch for verification...")
batch = client.verify_batch(emails, name='Example Batch')

batch_id = batch['id']
print(f"Batch ID: {batch_id}")
print(f"Total emails: {batch['total_emails']}")

# Poll for completion
print("\nChecking progress...")
while True:
    status = client.get_batch_status(batch_id)

    print(f"Status: {status['status']}")
    print(f"Progress: {status['progress']}%")
    print(f"Processed: {status['processed_emails']}/{status['total_emails']}")

    if status['status'] == 'completed':
        print(f"\nCompleted!")
        print(f"Valid: {status['valid_emails']}")
        print(f"Invalid: {status['invalid_emails']}")
        print(f"Unknown: {status['unknown_emails']}")
        break
    elif status['status'] == 'failed':
        print("\nBatch verification failed")
        break

    time.sleep(5)  # Wait 5 seconds before checking again

# Download results
print("\nDownloading results...")
results = client.get_batch_results(batch_id, format='json', filter='all')

print("\nResults:")
for email_data in results['data']:
    print(f"{email_data['email']}: {email_data['result']}")
