"""
Database Manager Module
Handles SQLite database operations for the Comcast Port Monitor
"""

import sqlite3
import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os

class DatabaseManager:
    def __init__(self, db_path: str = "port_monitor.db"):
        """
        Initialize the database manager
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create port_scans table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS port_scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    response_time_ms INTEGER,
                    error_message TEXT,
                    protocol_info TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create configuration table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuration (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_port_scans_timestamp 
                ON port_scans(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_port_scans_host_port 
                ON port_scans(host, port)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_port_scans_status 
                ON port_scans(status)
            ''')
            
            conn.commit()
    
    def save_scan_result(self, result: Dict) -> int:
        """
        Save a single scan result to the database
        
        Args:
            result: Scan result dictionary
            
        Returns:
            ID of the inserted record
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Convert protocol_info to JSON string if it exists
            protocol_info_json = None
            if result.get('protocol_info'):
                protocol_info_json = json.dumps(result['protocol_info'])
            
            cursor.execute('''
                INSERT INTO port_scans 
                (timestamp, host, port, status, response_time_ms, error_message, protocol_info)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                result['timestamp'],
                result['host'],
                result['port'],
                result['status'],
                result['response_time_ms'],
                result['error_message'],
                protocol_info_json
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def save_scan_results(self, results: List[Dict]) -> List[int]:
        """
        Save multiple scan results to the database
        
        Args:
            results: List of scan result dictionaries
            
        Returns:
            List of IDs of the inserted records
        """
        ids = []
        for result in results:
            record_id = self.save_scan_result(result)
            ids.append(record_id)
        return ids
    
    def get_recent_scans(self, limit: int = 100, host: str = None, port: int = None) -> List[Dict]:
        """
        Get recent scan results
        
        Args:
            limit: Maximum number of results to return
            host: Filter by host (optional)
            port: Filter by port (optional)
            
        Returns:
            List of scan result dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM port_scans 
                WHERE 1=1
            '''
            params = []
            
            if host:
                query += ' AND host = ?'
                params.append(host)
            
            if port:
                query += ' AND port = ?'
                params.append(port)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                result = dict(row)
                # Parse protocol_info JSON
                if result['protocol_info']:
                    try:
                        result['protocol_info'] = json.loads(result['protocol_info'])
                    except json.JSONDecodeError:
                        result['protocol_info'] = None
                results.append(result)
            
            return results
    
    def get_scans_by_timerange(self, start_time: datetime, end_time: datetime, 
                              host: str = None, port: int = None) -> List[Dict]:
        """
        Get scan results within a specific time range
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            host: Filter by host (optional)
            port: Filter by port (optional)
            
        Returns:
            List of scan result dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM port_scans 
                WHERE timestamp BETWEEN ? AND ?
            '''
            params = [start_time.isoformat(), end_time.isoformat()]
            
            if host:
                query += ' AND host = ?'
                params.append(host)
            
            if port:
                query += ' AND port = ?'
                params.append(port)
            
            query += ' ORDER BY timestamp ASC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                result = dict(row)
                if result['protocol_info']:
                    try:
                        result['protocol_info'] = json.loads(result['protocol_info'])
                    except json.JSONDecodeError:
                        result['protocol_info'] = None
                results.append(result)
            
            return results
    
    def get_24h_statistics(self, host: str = None) -> Dict:
        """
        Get statistics for the last 24 hours
        
        Args:
            host: Filter by host (optional)
            
        Returns:
            Dictionary containing statistics
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Base query conditions
            where_clause = "WHERE timestamp BETWEEN ? AND ?"
            params = [start_time.isoformat(), end_time.isoformat()]
            
            if host:
                where_clause += " AND host = ?"
                params.append(host)
            
            # Total scans
            cursor.execute(f'''
                SELECT COUNT(*) FROM port_scans {where_clause}
            ''', params)
            total_scans = cursor.fetchone()[0]
            
            # Successful scans
            cursor.execute(f'''
                SELECT COUNT(*) FROM port_scans 
                {where_clause} AND status = 'OPEN'
            ''', params)
            successful_scans = cursor.fetchone()[0]
            
            # Blocked ports (unique ports that were closed/timeout)
            cursor.execute(f'''
                SELECT COUNT(DISTINCT port) FROM port_scans 
                {where_clause} AND status IN ('CLOSED', 'TIMEOUT')
            ''', params)
            blocked_ports = cursor.fetchone()[0]
            
            # Average response time
            cursor.execute(f'''
                SELECT AVG(response_time_ms) FROM port_scans 
                {where_clause} AND status = 'OPEN'
            ''', params)
            avg_response = cursor.fetchone()[0] or 0
            
            # Calculate success rate
            success_rate = (successful_scans / total_scans * 100) if total_scans > 0 else 0
            
            return {
                'total_scans': total_scans,
                'successful_scans': successful_scans,
                'success_rate': success_rate,
                'blocked_ports': blocked_ports,
                'avg_response': avg_response
            }
    
    def get_chart_data(self, hours: int = None) -> List[Dict]:
        """
        Get data for chart visualization
        
        Args:
            hours: Number of hours to look back (None for all data)
            
        Returns:
            List of scan results for charting
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if hours:
                start_time = datetime.now() - timedelta(hours=hours)
                cursor.execute('''
                    SELECT timestamp, host, port, status, response_time_ms 
                    FROM port_scans 
                    WHERE timestamp >= ?
                    ORDER BY timestamp ASC
                ''', (start_time.isoformat(),))
            else:
                cursor.execute('''
                    SELECT timestamp, host, port, status, response_time_ms 
                    FROM port_scans 
                    ORDER BY timestamp ASC
                ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def save_configuration(self, config: Dict):
        """
        Save configuration settings
        
        Args:
            config: Configuration dictionary
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for key, value in config.items():
                # Convert value to JSON string if it's not a string
                if not isinstance(value, str):
                    value = json.dumps(value)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO configuration (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, value))
            
            conn.commit()
    
    def get_configuration(self) -> Dict:
        """
        Get all configuration settings
        
        Returns:
            Dictionary containing all configuration settings
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT key, value FROM configuration')
            rows = cursor.fetchall()
            
            config = {}
            for row in rows:
                key = row['key']
                value = row['value']
                
                # Try to parse JSON, fall back to string
                try:
                    config[key] = json.loads(value)
                except json.JSONDecodeError:
                    config[key] = value
            
            return config
    
    def get_configuration_value(self, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        config = self.get_configuration()
        return config.get(key, default)
    
    def export_to_csv(self, filename: str, days: int = 7):
        """
        Export scan data to CSV file
        
        Args:
            filename: Output CSV filename
            days: Number of days to export
        """
        start_time = datetime.now() - timedelta(days=days)
        end_time = datetime.now()
        
        data = self.get_scans_by_timerange(start_time, end_time)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if not data:
                return
            
            fieldnames = ['timestamp', 'host', 'port', 'status', 'response_time_ms', 'error_message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in data:
                # Remove protocol_info for CSV export (too complex)
                csv_row = {k: v for k, v in row.items() if k in fieldnames}
                writer.writerow(csv_row)
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """
        Remove old scan data to keep database size manageable
        
        Args:
            days_to_keep: Number of days of data to keep
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM port_scans 
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            # Vacuum to reclaim space
            cursor.execute('VACUUM')
            
            return deleted_count
    
    def get_database_stats(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Dictionary containing database statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total records
            cursor.execute('SELECT COUNT(*) FROM port_scans')
            total_records = cursor.fetchone()[0]
            
            # Date range
            cursor.execute('''
                SELECT MIN(timestamp), MAX(timestamp) FROM port_scans
            ''')
            date_range = cursor.fetchone()
            
            # Unique hosts
            cursor.execute('SELECT COUNT(DISTINCT host) FROM port_scans')
            unique_hosts = cursor.fetchone()[0]
            
            # Unique ports
            cursor.execute('SELECT COUNT(DISTINCT port) FROM port_scans')
            unique_ports = cursor.fetchone()[0]
            
            # Database file size
            file_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            return {
                'total_records': total_records,
                'earliest_record': date_range[0],
                'latest_record': date_range[1],
                'unique_hosts': unique_hosts,
                'unique_ports': unique_ports,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2)
            }

# Example usage and testing
if __name__ == "__main__":
    # Test the database manager
    db = DatabaseManager("test_port_monitor.db")
    
    # Test saving a scan result
    test_result = {
        'timestamp': datetime.now().isoformat(),
        'host': 'mail.comcast.net',
        'port': 25,
        'status': 'OPEN',
        'response_time_ms': 150,
        'error_message': None,
        'protocol_info': {'protocol': 'SMTP', 'test_result': 'SUCCESS'}
    }
    
    record_id = db.save_scan_result(test_result)
    print(f"Saved scan result with ID: {record_id}")
    
    # Test getting recent scans
    recent = db.get_recent_scans(limit=5)
    print(f"Recent scans: {len(recent)} records")
    
    # Test statistics
    stats = db.get_24h_statistics()
    print(f"24h statistics: {stats}")
    
    # Test configuration
    config = {'server': 'mail.comcast.net', 'interval': 60, 'ports': [25, 465, 587]}
    db.save_configuration(config)
    
    loaded_config = db.get_configuration()
    print(f"Configuration: {loaded_config}")
    
    # Test database stats
    db_stats = db.get_database_stats()
    print(f"Database stats: {db_stats}")
    
    # Cleanup test database
    os.remove("test_port_monitor.db") 