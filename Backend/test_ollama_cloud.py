"""
Test script for Ollama Cloud API support with environment variable configuration
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import OllamaLLM

def test_defaults():
    """Test default configuration (cloud with environment variables)"""
    print("\n=== Testing Default Configuration ===")
    llm = OllamaLLM()
    print(f"Model: {llm.model}")
    print(f"Base URL: {llm.base_url}")
    print(f"Temperature: {llm.temperature}")
    print(f"API Key: {'Set' if llm.api_key else 'Not Set'}")
    print(f"Headers: {llm.headers}")
    
def test_explicit_local():
    """Test explicit local Ollama instance"""
    print("\n=== Testing Explicit Local Instance ===")
    local_llm = OllamaLLM(
        model="qwen2.5:3b",
        base_url="http://localhost:11434",
        temperature=0.1
    )
    print(f"Model: {local_llm.model}")
    print(f"Base URL: {local_llm.base_url}")
    print(f"Temperature: {local_llm.temperature}")
    print(f"API Key: {'Set' if local_llm.api_key else 'Not Set'}")
    print(f"Headers: {local_llm.headers}")
    
def test_cloud_with_api_key():
    """Test cloud Ollama API with explicit API key"""
    print("\n=== Testing Cloud API (Explicit API Key) ===")
    cloud_llm = OllamaLLM(
        model="gpt-oss:120b",
        base_url="https://ollama.com/api",
        api_key="test-api-key-12345",
        temperature=0.1
    )
    print(f"Model: {cloud_llm.model}")
    print(f"Base URL: {cloud_llm.base_url}")
    print(f"Temperature: {cloud_llm.temperature}")
    print(f"API Key: {'Set' if cloud_llm.api_key else 'Not Set'}")
    print(f"Headers: {cloud_llm.headers}")
    
def test_env_variables():
    """Test configuration via environment variables"""
    print("\n=== Testing Environment Variable Configuration ===")
    
    # Set environment variables
    os.environ['OLLAMA_MODEL'] = 'llama2:7b'
    os.environ['OLLAMA_BASE_URL'] = 'https://custom-ollama.example.com'
    os.environ['TEMPERATURE'] = '0.5'
    os.environ['OLLAMA_API_KEY'] = 'env-api-key-67890'
    
    env_llm = OllamaLLM()
    print(f"Model: {env_llm.model}")
    print(f"Base URL: {env_llm.base_url}")
    print(f"Temperature: {env_llm.temperature}")
    print(f"API Key: {'Set' if env_llm.api_key else 'Not Set'}")
    print(f"Headers: {env_llm.headers}")
    
    # Clean up
    for key in ['OLLAMA_MODEL', 'OLLAMA_BASE_URL', 'TEMPERATURE', 'OLLAMA_API_KEY']:
        if key in os.environ:
            del os.environ[key]

def test_partial_override():
    """Test partial parameter override with environment fallbacks"""
    print("\n=== Testing Partial Override (model only) ===")
    
    os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
    os.environ['TEMPERATURE'] = '0.2'
    
    partial_llm = OllamaLLM(model="custom-model:latest")
    print(f"Model: {partial_llm.model} (from parameter)")
    print(f"Base URL: {partial_llm.base_url} (from env)")
    print(f"Temperature: {partial_llm.temperature} (from env)")
    
    # Clean up
    for key in ['OLLAMA_BASE_URL', 'TEMPERATURE']:
        if key in os.environ:
            del os.environ[key]

if __name__ == "__main__":
    print("Ollama Environment Variable Configuration - Test Suite")
    print("=" * 60)
    
    try:
        test_defaults()
        test_explicit_local()
        test_cloud_with_api_key()
        test_env_variables()
        test_partial_override()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All configuration tests completed!")
        print("\nConfiguration Priority:")
        print("1. Explicit parameters (highest)")
        print("2. Environment variables")
        print("3. Default values (lowest)")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
