# EmailListChecker Python SDK

[![PyPI version](https://img.shields.io/pypi/v/emaillistchecker.svg)](https://pypi.org/project/emaillistchecker/)
[![Python versions](https://img.shields.io/pypi/pyversions/emaillistchecker.svg)](https://pypi.org/project/emaillistchecker/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Official Python SDK for the [EmailListChecker](https://emaillistchecker.io) email verification API.

## Features

- **Email Verification** - Verify single or bulk email addresses
- **Email Finder** - Discover email addresses by name, domain, or company
- **Credit Management** - Check balance and usage
- **Batch Processing** - Async verification of large lists
- **Type Hints** - Full typing support for better IDE experience
- **Error Handling** - Comprehensive exception classes

## Installation

```bash
pip install emaillistchecker
```

## Quick Start

```python
from emaillistchecker import EmailListChecker

# Initialize client
client = EmailListChecker(api_key='your_api_key_here')

# Verify an email
result = client.verify('test@example.com')
print(f"Result: {result['result']}")  # deliverable, undeliverable, risky, unknown
print(f"Score: {result['score']}")     # 0.0 to 1.0
```

## Get Your API Key

1. Sign up at [platform.emaillistchecker.io](https://platform.emaillistchecker.io/register)
2. Get your API key from the [API Dashboard](https://platform.emaillistchecker.io/api)
3. Start verifying!

## Usage Examples

### Single Email Verification

```python
from emaillistchecker import EmailListChecker

client = EmailListChecker(api_key='your_api_key')

# Verify single email
result = client.verify('user@example.com')

if result['result'] == 'deliverable':
    print('✓ Email is valid and deliverable')
elif result['result'] == 'undeliverable':
    print('✗ Email is invalid')
elif result['result'] == 'risky':
    print('⚠ Email is risky (catch-all, disposable, etc.)')
else:
    print('? Unable to determine')

# Check details
print(f"Disposable: {result['disposable']}")
print(f"Role account: {result['role']}")
print(f"Free provider: {result['free']}")
print(f"SMTP provider: {result['smtp_provider']}")
```

### Batch Email Verification

```python
# Submit batch for verification
emails = [
    'user1@example.com',
    'user2@example.com',
    'user3@example.com'
]

batch = client.verify_batch(emails, name='My Campaign List')
batch_id = batch['id']

print(f"Batch ID: {batch_id}")
print(f"Status: {batch['status']}")

# Check progress
import time

while True:
    status = client.get_batch_status(batch_id)
    print(f"Progress: {status['progress']}%")

    if status['status'] == 'completed':
        break

    time.sleep(5)  # Wait 5 seconds before checking again

# Download results
results = client.get_batch_results(batch_id, format='json', filter='all')

for email_data in results['data']:
    print(f"{email_data['email']}: {email_data['result']}")
```

### Email Finder

```python
# Find email by name and domain
result = client.find_email(
    first_name='John',
    last_name='Doe',
    domain='example.com'
)

print(f"Found: {result['email']}")
print(f"Confidence: {result['confidence']}%")
print(f"Verified: {result['verified']}")

# Find all emails for a domain
domain_results = client.find_by_domain('example.com', limit=50)

for email in domain_results['emails']:
    print(f"{email['email']} - Last verified: {email['last_verified']}")

# Find emails by company name
company_results = client.find_by_company('Acme Corporation')

print(f"Possible domains: {company_results['possible_domains']}")
for email in company_results['emails']:
    print(f"{email['email']} ({email['domain']})")
```

### Credit Management

```python
# Check credit balance
credits = client.get_credits()
print(f"Available credits: {credits['balance']}")
print(f"Used this month: {credits['used_this_month']}")
print(f"Current plan: {credits['plan']}")

# Get usage statistics
usage = client.get_usage()
print(f"Total API calls: {usage['total_requests']}")
print(f"Successful: {usage['successful_requests']}")
print(f"Failed: {usage['failed_requests']}")
```

### List Management

```python
# Get all lists
lists = client.get_lists()

for lst in lists:
    print(f"ID: {lst['id']}")
    print(f"Name: {lst['name']}")
    print(f"Status: {lst['status']}")
    print(f"Total emails: {lst['total_emails']}")
    print(f"Valid: {lst['valid_emails']}")
    print("---")

# Delete a list
client.delete_list(list_id=123)
```

## Error Handling

```python
from emaillistchecker import (
    EmailListChecker,
    EmailListCheckerException,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    ValidationError
)

client = EmailListChecker(api_key='your_api_key')

try:
    result = client.verify('test@example.com')
except AuthenticationError:
    print('Invalid API key')
except InsufficientCreditsError:
    print('Not enough credits')
except RateLimitError as e:
    print(f'Rate limit exceeded. Retry after {e.status_code} seconds')
except ValidationError as e:
    print(f'Validation error: {e.message}')
except EmailListCheckerException as e:
    print(f'API error: {e.message}')
```

## API Response Format

### Verification Result

```python
{
    'email': 'user@example.com',
    'result': 'deliverable',  # deliverable | undeliverable | risky | unknown
    'reason': 'VALID',         # VALID | INVALID | ACCEPT_ALL | DISPOSABLE | etc.
    'disposable': False,       # Is temporary/disposable email
    'role': False,             # Is role-based (info@, support@, etc.)
    'free': False,             # Is free provider (gmail, yahoo, etc.)
    'score': 1.0,              # Deliverability score (0.0 - 1.0)
    'smtp_provider': 'google', # Email provider
    'mx_records': ['mx1.google.com', 'mx2.google.com'],
    'domain': 'example.com',
    'spam_trap': False,
    'mx_found': True
}
```

## Configuration

### Custom Timeout

```python
# Set custom timeout (default: 30 seconds)
client = EmailListChecker(
    api_key='your_api_key',
    timeout=60  # 60 seconds
)
```

### Custom Base URL

```python
# Use custom API endpoint (for testing or private instances)
client = EmailListChecker(
    api_key='your_api_key',
    base_url='https://custom-api.example.com/api/v1'
)
```

## Requirements

- Python 3.7+
- requests >= 2.25.0

## Support

- **Documentation**: [platform.emaillistchecker.io/api](https://platform.emaillistchecker.io/api)
- **Email**: support@emaillistchecker.io
- **Issues**: [GitHub Issues](https://github.com/Emaillistchecker-io/emaillistchecker-python/issues)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

Made with ❤️ by [EmailListChecker](https://emaillistchecker.io)
