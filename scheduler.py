"""
Monitoring Scheduler Module
Handles scheduled port scanning for the Comcast Port Monitor
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Optional, List, Callable
import schedule
import random

class MonitoringScheduler:
    def __init__(self, db_manager, port_scanner):
        """
        Initialize the monitoring scheduler
        
        Args:
            db_manager: DatabaseManager instance
            port_scanner: PortScanner instance
        """
        self.db_manager = db_manager
        self.port_scanner = port_scanner
        self.is_running = False
        self.scheduler_thread = None
        self.stop_event = threading.Event()
        
        # Default configuration
        self.target_host = "mail.comcast.net"
        self.scan_interval = 60  # minutes
        self.ports_to_scan = self.port_scanner.get_default_ports()
        
        # Callbacks for UI updates
        self.scan_complete_callback = None
        self.status_update_callback = None
        
        # Load configuration from database
        self.load_configuration()
        
    def load_configuration(self):
        """Load configuration from database"""
        config = self.db_manager.get_configuration()
        
        if config:
            self.target_host = config.get('server', self.target_host)
            self.scan_interval = config.get('interval', self.scan_interval)
            self.ports_to_scan = config.get('ports', self.ports_to_scan)
    
    def save_configuration(self):
        """Save current configuration to database"""
        config = {
            'server': self.target_host,
            'interval': self.scan_interval,
            'ports': self.ports_to_scan
        }
        self.db_manager.save_configuration(config)
    
    def set_scan_complete_callback(self, callback: Callable):
        """Set callback function to be called when scan completes"""
        self.scan_complete_callback = callback
    
    def set_status_update_callback(self, callback: Callable):
        """Set callback function for status updates"""
        self.status_update_callback = callback
    
    def start_monitoring(self):
        """Start the monitoring scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        # Clear any existing scheduled jobs
        schedule.clear()
        
        # Schedule the monitoring job with some randomization to avoid detection
        # Use a range around the specified interval (±5 minutes)
        min_interval = max(1, self.scan_interval - 5)
        max_interval = self.scan_interval + 5
        
        # Schedule with random intervals
        schedule.every(min_interval).to(max_interval).minutes.do(self._perform_scan)
        
        # Start the scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # Perform initial scan
        self._perform_scan()
        
        if self.status_update_callback:
            self.status_update_callback("Monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring scheduler"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.stop_event.set()
        
        # Clear scheduled jobs
        schedule.clear()
        
        # Wait for scheduler thread to finish
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        if self.status_update_callback:
            self.status_update_callback("Monitoring stopped")
    
    def scan_now(self):
        """Perform an immediate scan"""
        if not self.is_running:
            # If not running, just do a one-time scan
            self._perform_scan()
        else:
            # If running, schedule an immediate scan
            threading.Thread(target=self._perform_scan, daemon=True).start()
    
    def _run_scheduler(self):
        """Main scheduler loop running in separate thread"""
        while self.is_running and not self.stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"Scheduler error: {e}")
                if self.status_update_callback:
                    self.status_update_callback(f"Scheduler error: {e}")
    
    def _perform_scan(self):
        """Perform the actual port scan"""
        try:
            if self.status_update_callback:
                self.status_update_callback(f"Scanning {self.target_host}...")
            
            # Validate host before scanning
            if not self.port_scanner.validate_host(self.target_host):
                error_msg = f"Cannot resolve host: {self.target_host}"
                if self.status_update_callback:
                    self.status_update_callback(error_msg)
                return
            
            # Perform the scan
            results = self.port_scanner.scan_multiple_ports(self.target_host, self.ports_to_scan)
            
            # Save results to database
            self.db_manager.save_scan_results(results)
            
            # Log scan completion
            scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            open_ports = len([r for r in results if r['status'] == 'OPEN'])
            total_ports = len(results)
            
            status_msg = f"Scan completed at {scan_time}: {open_ports}/{total_ports} ports open"
            
            if self.status_update_callback:
                self.status_update_callback(status_msg)
            
            # Call scan complete callback if set
            if self.scan_complete_callback:
                self.scan_complete_callback(results)
            
            # Check for potential blocking patterns
            self._analyze_blocking_patterns(results)
            
        except Exception as e:
            error_msg = f"Scan failed: {str(e)}"
            print(error_msg)
            if self.status_update_callback:
                self.status_update_callback(error_msg)
    
    def _analyze_blocking_patterns(self, results: List[dict]):
        """Analyze scan results for potential blocking patterns"""
        blocked_ports = [r for r in results if r['status'] in ['CLOSED', 'TIMEOUT']]
        
        if blocked_ports:
            # Check if email ports are specifically being blocked
            email_ports = [25, 465, 587, 110, 995, 143, 993]
            blocked_email_ports = [r for r in blocked_ports if r['port'] in email_ports]
            
            if len(blocked_email_ports) >= 3:  # Threshold for suspicious blocking
                current_time = datetime.now()
                hour = current_time.hour
                
                # Log potential blocking event
                blocking_msg = (
                    f"POTENTIAL BLOCKING DETECTED at {current_time.strftime('%H:%M:%S')}: "
                    f"{len(blocked_email_ports)} email ports blocked"
                )
                
                if self.status_update_callback:
                    self.status_update_callback(blocking_msg)
                
                # You could add more sophisticated analysis here:
                # - Check if this is a recurring pattern at this time
                # - Compare with historical data
                # - Send alerts/notifications
    
    def get_next_scan_time(self) -> Optional[datetime]:
        """Get the next scheduled scan time"""
        if not self.is_running:
            return None
        
        next_run = schedule.next_run()
        return next_run if next_run else None
    
    def get_last_scan_time(self) -> Optional[datetime]:
        """Get the time of the last scan"""
        recent_scans = self.db_manager.get_recent_scans(limit=1, host=self.target_host)
        if recent_scans:
            return datetime.fromisoformat(recent_scans[0]['timestamp'])
        return None
    
    def update_configuration(self, host: str = None, interval: int = None, ports: List[int] = None):
        """Update monitoring configuration"""
        if host is not None:
            self.target_host = host
        
        if interval is not None:
            self.scan_interval = interval
        
        if ports is not None:
            self.ports_to_scan = ports
        
        # Save to database
        self.save_configuration()
        
        # If monitoring is running, restart with new configuration
        if self.is_running:
            self.stop_monitoring()
            time.sleep(1)  # Brief pause
            self.start_monitoring()
    
    def get_monitoring_status(self) -> dict:
        """Get current monitoring status"""
        return {
            'is_running': self.is_running,
            'target_host': self.target_host,
            'scan_interval': self.scan_interval,
            'ports_count': len(self.ports_to_scan),
            'ports': self.ports_to_scan,
            'next_scan': self.get_next_scan_time(),
            'last_scan': self.get_last_scan_time()
        }
    
    def get_scan_history_summary(self, hours: int = 24) -> dict:
        """Get a summary of scan history for the specified time period"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        scans = self.db_manager.get_scans_by_timerange(
            start_time, end_time, host=self.target_host
        )
        
        if not scans:
            return {
                'total_scans': 0,
                'unique_scan_sessions': 0,
                'success_rate': 0,
                'avg_response_time': 0,
                'blocked_ports': []
            }
        
        # Group scans by timestamp to count scan sessions
        scan_sessions = {}
        for scan in scans:
            timestamp = scan['timestamp'][:16]  # Group by minute
            if timestamp not in scan_sessions:
                scan_sessions[timestamp] = []
            scan_sessions[timestamp].append(scan)
        
        # Calculate statistics
        total_scans = len(scans)
        successful_scans = len([s for s in scans if s['status'] == 'OPEN'])
        success_rate = (successful_scans / total_scans * 100) if total_scans > 0 else 0
        
        response_times = [s['response_time_ms'] for s in scans if s['status'] == 'OPEN' and s['response_time_ms']]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Find consistently blocked ports
        port_stats = {}
        for scan in scans:
            port = scan['port']
            if port not in port_stats:
                port_stats[port] = {'total': 0, 'blocked': 0}
            port_stats[port]['total'] += 1
            if scan['status'] in ['CLOSED', 'TIMEOUT']:
                port_stats[port]['blocked'] += 1
        
        blocked_ports = []
        for port, stats in port_stats.items():
            block_rate = stats['blocked'] / stats['total']
            if block_rate > 0.5:  # More than 50% blocked
                blocked_ports.append({
                    'port': port,
                    'block_rate': block_rate * 100,
                    'total_attempts': stats['total']
                })
        
        return {
            'total_scans': total_scans,
            'unique_scan_sessions': len(scan_sessions),
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'blocked_ports': blocked_ports
        }
    
    def export_evidence_report(self, filename: str, days: int = 7):
        """Export a detailed evidence report for ISP dispute"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        scans = self.db_manager.get_scans_by_timerange(
            start_time, end_time, host=self.target_host
        )
        
        # Generate report content
        report_lines = [
            f"Comcast Email Port Monitoring Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Period: {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}",
            f"Target Server: {self.target_host}",
            f"",
            f"SUMMARY:",
            f"Total Scans: {len(scans)}",
            f"Monitoring Period: {days} days",
            f""
        ]
        
        # Analyze by port
        port_analysis = {}
        for scan in scans:
            port = scan['port']
            if port not in port_analysis:
                port_analysis[port] = {
                    'total': 0, 'open': 0, 'closed': 0, 'timeout': 0, 'error': 0
                }
            port_analysis[port]['total'] += 1
            port_analysis[port][scan['status'].lower()] += 1
        
        report_lines.append("PORT ANALYSIS:")
        for port in sorted(port_analysis.keys()):
            stats = port_analysis[port]
            success_rate = (stats['open'] / stats['total']) * 100
            protocol = self.port_scanner.get_port_description(port)
            
            report_lines.append(
                f"Port {port} ({protocol}): "
                f"{success_rate:.1f}% success rate "
                f"({stats['open']}/{stats['total']} successful)"
            )
        
        # Time-based analysis
        report_lines.extend([
            "",
            "TIME-BASED BLOCKING ANALYSIS:",
            "(Hours when ports were consistently blocked)"
        ])
        
        # Group by hour and analyze blocking patterns
        hourly_stats = {}
        for scan in scans:
            hour = datetime.fromisoformat(scan['timestamp']).hour
            if hour not in hourly_stats:
                hourly_stats[hour] = {'total': 0, 'blocked': 0}
            hourly_stats[hour]['total'] += 1
            if scan['status'] in ['CLOSED', 'TIMEOUT']:
                hourly_stats[hour]['blocked'] += 1
        
        for hour in sorted(hourly_stats.keys()):
            stats = hourly_stats[hour]
            block_rate = (stats['blocked'] / stats['total']) * 100
            if block_rate > 30:  # Significant blocking
                report_lines.append(
                    f"Hour {hour:02d}:00 - {block_rate:.1f}% blocking rate "
                    f"({stats['blocked']}/{stats['total']} attempts blocked)"
                )
        
        # Write report to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        return filename

# Example usage and testing
if __name__ == "__main__":
    from database import DatabaseManager
    from port_scanner import PortScanner
    
    # Create test instances
    db = DatabaseManager("test_scheduler.db")
    scanner = PortScanner(timeout=5)
    scheduler = MonitoringScheduler(db, scanner)
    
    # Set up callbacks
    def on_scan_complete(results):
        print(f"Scan completed: {len(results)} ports scanned")
        for result in results:
            print(f"  Port {result['port']}: {result['status']}")
    
    def on_status_update(message):
        print(f"Status: {message}")
    
    scheduler.set_scan_complete_callback(on_scan_complete)
    scheduler.set_status_update_callback(on_status_update)
    
    # Test configuration
    scheduler.update_configuration(
        host="mail.comcast.net",
        interval=1,  # 1 minute for testing
        ports=[25, 80, 443]
    )
    
    print("Starting monitoring...")
    scheduler.start_monitoring()
    
    # Let it run for a bit
    time.sleep(70)  # Run for just over a minute to see one scheduled scan
    
    print("Stopping monitoring...")
    scheduler.stop_monitoring()
    
    # Get status
    status = scheduler.get_monitoring_status()
    print(f"Final status: {status}")
    
    # Get history summary
    history = scheduler.get_scan_history_summary(hours=1)
    print(f"History summary: {history}")
    
    # Cleanup
    import os
    os.remove("test_scheduler.db") 