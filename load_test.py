import asyncio
import aiohttp
import time
import json
from statistics import mean, median
import argparse

class LoadTester:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self.results = []
    
    async def send_request(self, session: aiohttp.ClientSession, payload: dict) -> dict:
        """Send a single request"""
        start_time = time.time()
        
        try:
            async with session.post(
                f"{self.base_url}/api/v1/hackrx/run",
                headers=self.headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                end_time = time.time()
                
                result = {
                    'status_code': response.status,
                    'response_time': end_time - start_time,
                    'success': response.status == 200,
                    'timestamp': start_time
                }
                
                if response.status == 200:
                    response_data = await response.json()
                    result['answers_count'] = len(response_data.get('answers', []))
                else:
                    result['error'] = await response.text()
                
                return result
                
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': time.time() - start_time,
                'success': False,
                'error': str(e),
                'timestamp': start_time
            }
    
    async def run_load_test(self, concurrent_users: int, requests_per_user: int, test_payload: dict):
        """Run load test with specified parameters"""
        print(f"Starting load test: {concurrent_users} users, {requests_per_user} requests each")
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for user in range(concurrent_users):
                for request in range(requests_per_user):
                    task = self.send_request(session, test_payload)
                    tasks.append(task)
            
            # Execute all requests
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = [r for r in results if isinstance(r, dict)]
            self.results.extend(valid_results)
            
            return valid_results
    
    def generate_report(self) -> dict:
        """Generate test report"""
        if not self.results:
            return {"error": "No results to analyze"}
        
        successful_requests = [r for r in self.results if r['success']]
        failed_requests = [r for r in self.results if not r['success']]
        
        response_times = [r['response_time'] for r in successful_requests]
        
        report = {
            'summary': {
                'total_requests': len(self.results),
                'successful_requests': len(successful_requests),
                'failed_requests': len(failed_requests),
                'success_rate': len(successful_requests) / len(self.results) * 100
            },
            'performance': {
                'avg_response_time': mean(response_times) if response_times else 0,
                'median_response_time': median(response_times) if response_times else 0,
                'min_response_time': min(response_times) if response_times else 0,
                'max_response_time': max(response_times) if response_times else 0,
                'requests_per_second': len(successful_requests) / max(response_times) if response_times else 0
            },
            'errors': {}
        }
        
        # Analyze errors
        for result in failed_requests:
            error_type = result.get('error', 'Unknown')[:50]
            if error_type in report['errors']:
                report['errors'][error_type] += 1
            else:
                report['errors'][error_type] = 1
        
        return report

async def main():
    parser = argparse.ArgumentParser(description='Load test the API')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL')
    parser.add_argument('--token', required=True, help='API token')
    parser.add_argument('--users', type=int, default=5, help='Concurrent users')
    parser.add_argument('--requests', type=int, default=10, help='Requests per user')
    
    args = parser.parse_args()
    
    # Test payload
    test_payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?"
        ]
    }
    
    # Run load test
    tester = LoadTester(args.url, args.token)
    await tester.run_load_test(args.users, args.requests, test_payload)
    
    # Generate and save report
    report = tester.generate_report()
    
    with open('load_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("Load Test Results:")
    print(f"Total Requests: {report['summary']['total_requests']}")
    print(f"Success Rate: {report['summary']['success_rate']:.2f}%")
    print(f"Average Response Time: {report['performance']['avg_response_time']:.2f}s")
    print(f"Requests/Second: {report['performance']['requests_per_second']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())