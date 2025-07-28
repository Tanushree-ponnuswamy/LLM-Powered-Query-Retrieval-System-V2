import psutil
import time
import logging
from datetime import datetime
import json

class PerformanceMonitor:
    def __init__(self, log_file="performance.log"):
        self.log_file = log_file
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
    
    def get_system_metrics(self):
        """Get system performance metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": dict(psutil.net_io_counters()._asdict()),
            "process_count": len(psutil.pids())
        }
    
    def log_metrics(self):
        """Log current system metrics"""
        metrics = self.get_system_metrics()
        logging.info(f"METRICS: {json.dumps(metrics)}")
        return metrics
    
    def monitor_continuous(self, interval=60):
        """Continuously monitor system metrics"""
        print(f"Starting continuous monitoring (interval: {interval}s)")
        
        while True:
            try:
                metrics = self.log_metrics()
                print(f"CPU: {metrics['cpu_percent']:.1f}% | "
                      f"Memory: {metrics['memory_percent']:.1f}% | "
                      f"Disk: {metrics['disk_usage']:.1f}%")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\nMonitoring stopped")
                break
            except Exception as e:
                print(f"Error in monitoring: {e}")
                time.sleep(interval)

if __name__ == "__main__":
    monitor = PerformanceMonitor()
    monitor.monitor_continuous()