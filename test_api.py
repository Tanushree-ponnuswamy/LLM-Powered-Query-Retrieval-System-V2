import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_TOKEN = "59d150e97f686fcc6859251c02b719e661203b21d4fb2eae792e07e727f07bff"

def test_health_check():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_query_processing():
    """Test query processing endpoint"""
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?"
        ]
    }
    
    print("Testing query processing...")
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/api/v1/hackrx/run",
        headers=headers,
        json=payload,
        timeout=60
    )
    
    end_time = time.time()
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {end_time - start_time:.2f} seconds")
    
    if response.status_code == 200:
        result = response.json()
        print("Answers:")
        for i, answer in enumerate(result["answers"]):
            print(f"{i+1}. {answer}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def main():
    """Run all tests"""
    print("Starting API Tests...")
    
    # Test health check
    if not test_health_check():
        print("Health check failed!")
        return
    
    print("\n" + "="*50 + "\n")
    
    # Test query processing
    if not test_query_processing():
        print("Query processing test failed!")
        return
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    main()