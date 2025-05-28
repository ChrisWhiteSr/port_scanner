"""
Port Scanner Module
Handles port scanning functionality for the Comcast Port Monitor
"""

import socket
import threading
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import smtplib
import poplib
import imaplib
import requests
from typing import Dict, List, Tuple, Optional

class PortScanner:
    def __init__(self, timeout: int = 10, max_workers: int = 10):
        """
        Initialize the port scanner
        
        Args:
            timeout: Connection timeout in seconds
            max_workers: Maximum number of concurrent scanning threads
        """
        self.timeout = timeout
        self.max_workers = max_workers
        
    def scan_port(self, host: str, port: int) -> Dict:
        """
        Scan a single port and return detailed results
        
        Args:
            host: Target hostname or IP address
            port: Port number to scan
            
        Returns:
            Dictionary containing scan results
        """
        start_time = time.time()
        result = {
            'host': host,
            'port': port,
            'status': 'UNKNOWN',
            'response_time_ms': 0,
            'timestamp': datetime.now().isoformat(),
            'error_message': None,
            'protocol_info': None
        }
        
        try:
            # Basic TCP connection test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            connection_result = sock.connect_ex((host, port))
            response_time = (time.time() - start_time) * 1000
            
            if connection_result == 0:
                result['status'] = 'OPEN'
                result['response_time_ms'] = int(response_time)
                
                # Try protocol-specific testing
                protocol_info = self._test_protocol(host, port, sock)
                if protocol_info:
                    result['protocol_info'] = protocol_info
                    
            else:
                result['status'] = 'CLOSED'
                result['response_time_ms'] = int(response_time)
                
            sock.close()
            
        except socket.timeout:
            result['status'] = 'TIMEOUT'
            result['response_time_ms'] = self.timeout * 1000
            result['error_message'] = 'Connection timeout'
            
        except socket.gaierror as e:
            result['status'] = 'ERROR'
            result['error_message'] = f'DNS resolution failed: {str(e)}'
            
        except Exception as e:
            result['status'] = 'ERROR'
            result['error_message'] = str(e)
            
        return result
    
    def scan_multiple_ports(self, host: str, ports: List[int]) -> List[Dict]:
        """
        Scan multiple ports concurrently
        
        Args:
            host: Target hostname or IP address
            ports: List of port numbers to scan
            
        Returns:
            List of scan results
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scanning tasks
            future_to_port = {
                executor.submit(self.scan_port, host, port): port 
                for port in ports
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_port):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    port = future_to_port[future]
                    results.append({
                        'host': host,
                        'port': port,
                        'status': 'ERROR',
                        'response_time_ms': 0,
                        'timestamp': datetime.now().isoformat(),
                        'error_message': f'Scanning error: {str(e)}',
                        'protocol_info': None
                    })
        
        # Sort results by port number
        results.sort(key=lambda x: x['port'])
        return results
    
    def _test_protocol(self, host: str, port: int, sock: socket.socket) -> Optional[Dict]:
        """
        Test protocol-specific functionality for open ports
        
        Args:
            host: Target hostname
            port: Port number
            sock: Open socket connection
            
        Returns:
            Protocol information if available
        """
        try:
            if port in [25, 465, 587]:  # SMTP ports
                return self._test_smtp(host, port)
            elif port in [110, 995]:    # POP3 ports
                return self._test_pop3(host, port)
            elif port in [143, 993]:    # IMAP ports
                return self._test_imap(host, port)
            elif port in [80, 443]:     # HTTP/HTTPS ports
                return self._test_http(host, port)
        except Exception as e:
            return {'protocol_test': 'FAILED', 'error': str(e)}
        
        return None
    
    def _test_smtp(self, host: str, port: int) -> Dict:
        """Test SMTP protocol functionality"""
        try:
            if port == 465:  # SMTP SSL
                server = smtplib.SMTP_SSL(host, port, timeout=self.timeout)
            else:  # SMTP or SMTP TLS
                server = smtplib.SMTP(host, port, timeout=self.timeout)
                if port == 587:  # Try STARTTLS for port 587
                    server.starttls()
            
            # Get server greeting
            greeting = server.ehlo_or_helo_if_needed()
            server.quit()
            
            return {
                'protocol': 'SMTP',
                'test_result': 'SUCCESS',
                'server_response': str(greeting) if greeting else 'Connected'
            }
            
        except Exception as e:
            return {
                'protocol': 'SMTP',
                'test_result': 'FAILED',
                'error': str(e)
            }
    
    def _test_pop3(self, host: str, port: int) -> Dict:
        """Test POP3 protocol functionality"""
        try:
            if port == 995:  # POP3 SSL
                server = poplib.POP3_SSL(host, port, timeout=self.timeout)
            else:  # POP3
                server = poplib.POP3(host, port, timeout=self.timeout)
            
            # Get server greeting
            greeting = server.getwelcome()
            server.quit()
            
            return {
                'protocol': 'POP3',
                'test_result': 'SUCCESS',
                'server_response': greeting.decode('utf-8') if isinstance(greeting, bytes) else str(greeting)
            }
            
        except Exception as e:
            return {
                'protocol': 'POP3',
                'test_result': 'FAILED',
                'error': str(e)
            }
    
    def _test_imap(self, host: str, port: int) -> Dict:
        """Test IMAP protocol functionality"""
        try:
            if port == 993:  # IMAP SSL
                server = imaplib.IMAP4_SSL(host, port)
            else:  # IMAP
                server = imaplib.IMAP4(host, port)
            
            # Get server greeting
            greeting = server.response('OK')
            server.logout()
            
            return {
                'protocol': 'IMAP',
                'test_result': 'SUCCESS',
                'server_response': str(greeting)
            }
            
        except Exception as e:
            return {
                'protocol': 'IMAP',
                'test_result': 'FAILED',
                'error': str(e)
            }
    
    def _test_http(self, host: str, port: int) -> Dict:
        """Test HTTP/HTTPS protocol functionality"""
        try:
            protocol = 'https' if port == 443 else 'http'
            url = f"{protocol}://{host}:{port}"
            
            response = requests.head(url, timeout=self.timeout, allow_redirects=True)
            
            return {
                'protocol': protocol.upper(),
                'test_result': 'SUCCESS',
                'status_code': response.status_code,
                'server_header': response.headers.get('Server', 'Unknown')
            }
            
        except Exception as e:
            return {
                'protocol': 'HTTP/HTTPS',
                'test_result': 'FAILED',
                'error': str(e)
            }
    
    def get_default_ports(self) -> List[int]:
        """Get the default list of ports to monitor"""
        return [25, 465, 587, 110, 995, 143, 993, 80, 443]
    
    def get_email_ports(self) -> List[int]:
        """Get only email-related ports"""
        return [25, 465, 587, 110, 995, 143, 993]
    
    def get_web_ports(self) -> List[int]:
        """Get only web-related ports"""
        return [80, 443]
    
    def validate_host(self, host: str) -> bool:
        """
        Validate if a hostname is reachable
        
        Args:
            host: Hostname to validate
            
        Returns:
            True if host is reachable, False otherwise
        """
        try:
            socket.gethostbyname(host)
            return True
        except socket.gaierror:
            return False
    
    def get_port_description(self, port: int) -> str:
        """
        Get a human-readable description for a port
        
        Args:
            port: Port number
            
        Returns:
            Description string
        """
        descriptions = {
            25: "SMTP (Simple Mail Transfer Protocol)",
            465: "SMTP over SSL/TLS",
            587: "SMTP with STARTTLS",
            110: "POP3 (Post Office Protocol v3)",
            995: "POP3 over SSL/TLS",
            143: "IMAP (Internet Message Access Protocol)",
            993: "IMAP over SSL/TLS",
            80: "HTTP (Hypertext Transfer Protocol)",
            443: "HTTPS (HTTP over SSL/TLS)"
        }
        
        return descriptions.get(port, f"Custom port {port}")

# Example usage and testing
if __name__ == "__main__":
    scanner = PortScanner()
    
    # Test with Comcast mail server
    host = "mail.comcast.net"
    ports = scanner.get_default_ports()
    
    print(f"Scanning {host} on ports: {ports}")
    results = scanner.scan_multiple_ports(host, ports)
    
    for result in results:
        status_color = "🟢" if result['status'] == 'OPEN' else "🔴" if result['status'] == 'CLOSED' else "🟡"
        print(f"{status_color} Port {result['port']}: {result['status']} ({result['response_time_ms']}ms)")
        
        if result['protocol_info']:
            print(f"   Protocol: {result['protocol_info']}")
        if result['error_message']:
            print(f"   Error: {result['error_message']}") 