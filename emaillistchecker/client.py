"""EmailListChecker API Client"""

import requests
import time
from typing import Dict, List, Optional, Union
from .exceptions import (
    EmailListCheckerException,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    ValidationError,
    APIError
)


class EmailListChecker:
    """
    EmailListChecker API Client

    This class provides methods to interact with the EmailListChecker API.

    Args:
        api_key (str): Your EmailListChecker API key
        base_url (str): API base URL (default: https://platform.emaillistchecker.io/api/v1)
        timeout (int): Request timeout in seconds (default: 30)

    Example:
        >>> client = EmailListChecker(api_key='your_api_key')
        >>> result = client.verify('test@example.com')
        >>> print(result['result'])  # 'deliverable', 'undeliverable', 'risky', 'unknown'
    """

    def __init__(self, api_key: str, base_url: str = "https://platform.emaillistchecker.io/api/v1", timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'EmailListChecker-Python/1.0.0'
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request to API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=kwargs.pop('timeout', self.timeout),
                **kwargs
            )

            # Handle rate limiting with retry
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                raise RateLimitError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds",
                    status_code=429,
                    response=response.json() if response.content else None
                )

            # Parse response
            data = response.json() if response.content else {}

            # Handle errors
            if response.status_code == 401:
                raise AuthenticationError(
                    data.get('error', 'Invalid API key'),
                    status_code=401,
                    response=data
                )
            elif response.status_code == 402:
                raise InsufficientCreditsError(
                    data.get('error', 'Insufficient credits'),
                    status_code=402,
                    response=data
                )
            elif response.status_code == 422:
                raise ValidationError(
                    data.get('message', 'Validation error'),
                    status_code=422,
                    response=data
                )
            elif not response.ok:
                raise APIError(
                    data.get('error', f'API error: {response.status_code}'),
                    status_code=response.status_code,
                    response=data
                )

            return data

        except requests.exceptions.Timeout:
            raise EmailListCheckerException(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise EmailListCheckerException(f"Request failed: {str(e)}")

    def verify(self, email: str, timeout: Optional[int] = None, smtp_check: bool = True) -> Dict:
        """
        Verify a single email address

        Args:
            email (str): Email address to verify
            timeout (int, optional): Verification timeout in seconds (5-60)
            smtp_check (bool): Perform SMTP verification (default: True)

        Returns:
            dict: Verification result with keys:
                - email: Email address verified
                - result: 'deliverable', 'undeliverable', 'risky', 'unknown'
                - reason: Reason code (VALID, INVALID, etc.)
                - disposable: Is disposable email (bool)
                - role: Is role-based email (bool)
                - free: Is free email provider (bool)
                - score: Deliverability score (0-1)
                - smtp_provider: Email provider name
                - mx_records: List of MX records
                - domain: Email domain

        Example:
            >>> result = client.verify('user@example.com')
            >>> if result['result'] == 'deliverable':
            ...     print('Email is valid!')
        """
        params = {'email': email, 'smtp_check': smtp_check}
        if timeout:
            params['timeout'] = timeout

        response = self._request('POST', '/verify', json=params)
        return response.get('data', response)

    def verify_batch(self, emails: List[str], name: Optional[str] = None,
                    callback_url: Optional[str] = None, auto_start: bool = True) -> Dict:
        """
        Submit emails for batch verification

        Args:
            emails (list): List of email addresses (max 10,000)
            name (str, optional): Name for this batch
            callback_url (str, optional): Webhook URL for completion notification
            auto_start (bool): Start verification immediately (default: True)

        Returns:
            dict: Batch submission result with keys:
                - id: Batch ID
                - status: 'pending', 'processing', 'completed', 'failed'
                - total_emails: Total emails in batch
                - created_at: Creation timestamp

        Example:
            >>> batch = client.verify_batch(['email1@test.com', 'email2@test.com'])
            >>> batch_id = batch['id']
        """
        data = {
            'emails': emails,
            'auto_start': auto_start
        }
        if name:
            data['name'] = name
        if callback_url:
            data['callback_url'] = callback_url

        response = self._request('POST', '/verify/batch', json=data)
        return response.get('data', response)

    def verify_batch_file(self, file, name: Optional[str] = None,
                         callback_url: Optional[str] = None, auto_start: bool = True) -> Dict:
        """
        Upload file for batch verification (CSV, TXT, or XLSX)

        Args:
            file: File object or path to file (CSV, TXT, or XLSX)
            name (str, optional): Name for this batch
            callback_url (str, optional): Webhook URL for completion notification
            auto_start (bool): Start verification immediately (default: True)

        Returns:
            dict: Batch submission result with keys:
                - id: Batch ID
                - status: 'pending', 'processing', 'completed', 'failed'
                - total_emails: Total emails in batch
                - filename: Original filename
                - created_at: Creation timestamp

        Example:
            >>> with open('emails.csv', 'rb') as f:
            ...     batch = client.verify_batch_file(f, name='My List')
            >>> batch_id = batch['id']
        """
        # Prepare form data
        files = {}
        data = {'auto_start': str(auto_start).lower()}

        if name:
            data['name'] = name
        if callback_url:
            data['callback_url'] = callback_url

        # Handle file input
        if isinstance(file, str):
            # If file is a path string, open it
            files['file'] = open(file, 'rb')
        else:
            # Assume it's already a file object
            files['file'] = file

        # Temporarily remove Content-Type header for multipart/form-data
        headers = {'Authorization': f'Bearer {self.api_key}'}

        try:
            url = f"{self.base_url}/verify/batch/upload"
            response = requests.post(
                url,
                headers=headers,
                files=files,
                data=data,
                timeout=self.timeout
            )

            # Handle response
            response_data = response.json() if response.content else {}

            if response.status_code == 401:
                raise AuthenticationError(
                    response_data.get('error', 'Invalid API key'),
                    status_code=401,
                    response=response_data
                )
            elif response.status_code == 402:
                raise InsufficientCreditsError(
                    response_data.get('error', 'Insufficient credits'),
                    status_code=402,
                    response=response_data
                )
            elif response.status_code == 422:
                raise ValidationError(
                    response_data.get('message', 'Validation error'),
                    status_code=422,
                    response=response_data
                )
            elif not response.ok:
                raise APIError(
                    response_data.get('error', f'API error: {response.status_code}'),
                    status_code=response.status_code,
                    response=response_data
                )

            return response_data.get('data', response_data)

        finally:
            # Close file if we opened it
            if isinstance(file, str) and 'file' in files:
                files['file'].close()

    def get_batch_status(self, batch_id: int) -> Dict:
        """
        Get batch verification status

        Args:
            batch_id (int): Batch ID

        Returns:
            dict: Batch status with keys:
                - id: Batch ID
                - status: Current status
                - progress: Progress percentage (0-100)
                - total_emails: Total emails
                - processed_emails: Processed count
                - valid_emails: Valid count
                - invalid_emails: Invalid count
                - unknown_emails: Unknown count

        Example:
            >>> status = client.get_batch_status(123)
            >>> print(f"Progress: {status['progress']}%")
        """
        response = self._request('GET', f'/verify/batch/{batch_id}')
        return response.get('data', response)

    def get_batch_results(self, batch_id: int, format: str = 'json',
                         filter: str = 'all') -> Union[Dict, str]:
        """
        Download batch verification results

        Args:
            batch_id (int): Batch ID
            format (str): Output format - 'json', 'csv', 'txt' (default: 'json')
            filter (str): Filter results - 'all', 'valid', 'invalid', 'risky', 'unknown'

        Returns:
            dict or str: Results in requested format

        Example:
            >>> results = client.get_batch_results(123, format='json', filter='valid')
            >>> for email in results['data']:
            ...     print(email['email'])
        """
        params = {'format': format, 'filter': filter}
        response = self._request('GET', f'/verify/batch/{batch_id}/results', params=params)

        if format == 'json':
            return response.get('data', response)
        else:
            return response  # CSV or TXT as string

    def find_email(self, first_name: str, last_name: str, domain: str) -> Dict:
        """
        Find email address by name and domain

        Args:
            first_name (str): First name
            last_name (str): Last name
            domain (str): Domain (e.g., 'example.com')

        Returns:
            dict: Found email with keys:
                - email: Most likely email address
                - confidence: Confidence score (0-100)
                - pattern: Email pattern used
                - verified: Is verified in database (bool)
                - alternatives: List of alternative patterns

        Example:
            >>> result = client.find_email('John', 'Doe', 'example.com')
            >>> print(result['email'])  # john.doe@example.com
        """
        data = {
            'first_name': first_name,
            'last_name': last_name,
            'domain': domain
        }
        response = self._request('POST', '/finder/email', json=data)
        return response.get('data', response)

    def find_by_domain(self, domain: str, limit: int = 10, offset: int = 0) -> Dict:
        """
        Find emails by domain

        Args:
            domain (str): Domain to search
            limit (int): Results per request (1-100, default: 10)
            offset (int): Pagination offset (default: 0)

        Returns:
            dict: Found emails with keys:
                - domain: Searched domain
                - emails: List of found emails
                - patterns: Common email patterns for domain
                - total_found: Total emails found

        Example:
            >>> result = client.find_by_domain('example.com', limit=50)
            >>> for email in result['emails']:
            ...     print(email['email'])
        """
        data = {'domain': domain, 'limit': limit, 'offset': offset}
        response = self._request('POST', '/finder/domain', json=data)
        return response.get('data', response)

    def find_by_company(self, company: str, limit: int = 10) -> Dict:
        """
        Find emails by company name

        Args:
            company (str): Company name
            limit (int): Results limit (1-100, default: 10)

        Returns:
            dict: Found emails with keys:
                - company: Company name
                - possible_domains: Likely domains
                - emails: Found emails
                - total_found: Total found

        Example:
            >>> result = client.find_by_company('Acme Corporation')
            >>> print(result['emails'])
        """
        data = {'company': company, 'limit': limit}
        response = self._request('POST', '/finder/company', json=data)
        return response.get('data', response)

    def get_credits(self) -> Dict:
        """
        Get current credit balance

        Returns:
            dict: Credit information with keys:
                - balance: Current balance
                - used_this_month: Credits used this month
                - plan: Current plan name

        Example:
            >>> credits = client.get_credits()
            >>> print(f"Balance: {credits['balance']}")
        """
        response = self._request('GET', '/credits')
        return response.get('data', response)

    def get_usage(self) -> Dict:
        """
        Get API usage statistics

        Returns:
            dict: Usage statistics

        Example:
            >>> usage = client.get_usage()
            >>> print(f"Total requests: {usage['total_requests']}")
        """
        response = self._request('GET', '/usage')
        return response.get('data', response)

    def get_lists(self) -> List[Dict]:
        """
        Get all verification lists

        Returns:
            list: List of verification batches

        Example:
            >>> lists = client.get_lists()
            >>> for lst in lists:
            ...     print(f"{lst['name']}: {lst['status']}")
        """
        response = self._request('GET', '/lists')
        return response.get('data', response)

    def delete_list(self, list_id: int) -> Dict:
        """
        Delete a verification list

        Args:
            list_id (int): List ID to delete

        Returns:
            dict: Deletion confirmation

        Example:
            >>> client.delete_list(123)
        """
        response = self._request('DELETE', f'/lists/{list_id}')
        return response
