#!/usr/bin/env python3
"""
Test script for the intelligent LLM routing service
"""
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.routing_service import routing_service

def test_routing_classification():
    """Test the routing service classification"""
    
    print("🧪 Testing Intelligent LLM Routing Service")
    print("=" * 50)
    
    # Test cases with expected classifications
    test_cases = [
        # Simple queries
        ("Hello", "simple"),
        ("Hi there", "simple"),
        ("Thank you", "simple"),
        ("What time is it?", "simple"),
        ("Yes", "simple"),
        ("Good morning", "simple"),
        
        # Complex queries
        ("Analyze the crop yield trends for the last 5 years", "complex"),
        ("Explain machine learning algorithms for agriculture", "complex"),
        ("Calculate the ROI for organic farming investment", "complex"),
        ("Write a detailed financial report", "complex"),
        ("How can I optimize my irrigation system using data analysis?", "complex"),
        
        # Medium queries (could go either way)
        ("What's the weather like?", "simple"),
        ("How do I plant tomatoes?", "complex"),
        ("What crops grow well in monsoon?", "complex"),
    ]
    
    print("Testing query classification:")
    print("-" * 30)
    
    for query, expected in test_cases:
        classification, confidence = routing_service.classify_request_complexity(query)
        use_small = routing_service.should_use_small_llm(query)
        routing_info = routing_service.get_routing_info(query)
        
        status = "✅" if classification == expected else "⚠️"
        
        print(f"{status} Query: '{query[:40]}{'...' if len(query) > 40 else ''}'")
        print(f"   Classification: {classification} (confidence: {confidence:.2f})")
        print(f"   Use small LLM: {use_small}")
        print(f"   Word count: {routing_info['word_count']}")
        print()

def test_routing_service_integration():
    """Test the routing service integration"""
    
    print("🔧 Testing Routing Service Integration")
    print("=" * 50)
    
    # Test getting appropriate LLM
    test_queries = [
        "Hello",
        "Analyze agricultural data trends for better crop management"
    ]
    
    for query in test_queries:
        try:
            llm, model_type = routing_service.get_appropriate_llm(query)
            print(f"Query: '{query[:50]}{'...' if len(query) > 50 else ''}'")
            print(f"Selected model type: {model_type}")
            print(f"LLM instance: {type(llm).__name__}")
            print()
        except Exception as e:
            print(f"❌ Error getting LLM for query '{query}': {e}")
            print()

def test_routing_info():
    """Test detailed routing information"""
    
    print("📊 Testing Detailed Routing Information")
    print("=" * 50)
    
    query = "How can I use machine learning to predict crop yields and optimize my farming operations?"
    
    info = routing_service.get_routing_info(query)
    
    print(f"Query: '{query}'")
    print(f"Message length: {info['message_length']}")
    print(f"Word count: {info['word_count']}")
    print(f"Classification: {info['classification']}")
    print(f"Confidence: {info['confidence']:.2f}")
    print(f"Use small LLM: {info['use_small_llm']}")
    print(f"Selected model: {info['selected_model']}")

if __name__ == "__main__":
    try:
        test_routing_classification()
        test_routing_service_integration()
        test_routing_info()
        
        print("🎉 All routing service tests completed!")
        print("\n💡 Tips:")
        print("- Configure SMALL_LLM_* environment variables for dual-model setup")
        print("- Monitor routing decisions in production for optimization")
        print("- Adjust classification patterns based on your use case")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()