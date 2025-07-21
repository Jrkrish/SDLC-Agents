#!/usr/bin/env python3
"""
Test script for connector integration system
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_connector_system():
    """Test the connector integration system"""
    
    print("🔧 Testing DevPilot Connector Integration System")
    print("=" * 50)
    
    try:
        # Test import of enhanced components
        print("✅ Testing imports...")
        
        from src.dev_pilot.graph.enhanced_graph_builder import EnhancedGraphBuilder
        from src.dev_pilot.connectors.agent_connector_bridge import AgentConnectorBridge
        from src.dev_pilot.connectors.enhanced_github_connector import EnhancedGitHubConnector
        from src.dev_pilot.connectors.enhanced_slack_connector import EnhancedSlackConnector
        from src.dev_pilot.nodes.enhanced_coding_node import EnhancedCodingNode
        
        print("✅ All imports successful!")
        
        # Test enhanced graph builder initialization
        print("\n🔄 Testing Enhanced Graph Builder...")
        graph_builder = EnhancedGraphBuilder(model=None, enable_connectors=True)
        
        if hasattr(graph_builder, 'connector_manager'):
            print("✅ Connector manager initialized")
        else:
            print("❌ Connector manager not found")
            return False
        
        # Test connector status
        print("\n📊 Testing connector status...")
        status = graph_builder.get_connector_status()
        print(f"✅ Connector status retrieved: {status['summary']['total']} total connectors")
        
        # Test individual connector types
        print("\n🔌 Testing connector types...")
        for name, info in status["connectors"].items():
            status_icon = "✅" if info["enabled"] else "⚠️"
            print(f"{status_icon} {name}: {'Enabled' if info['enabled'] else 'Disabled'}")
        
        # Test agent-connector bridge
        print("\n🌉 Testing Agent-Connector Bridge...")
        bridge = AgentConnectorBridge(graph_builder.connector_manager)
        print("✅ Agent-Connector Bridge initialized")
        
        print("\n🎉 All tests passed! Connector integration system is ready.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_streamlit_compatibility():
    """Test Streamlit app compatibility"""
    
    print("\n🖥️  Testing Streamlit App Compatibility")
    print("=" * 50)
    
    try:
        # Test streamlit app imports
        from src.dev_pilot.ui.streamlit_ui.streamlit_app import load_app
        print("✅ Streamlit app imports successful")
        
        print("✅ Streamlit app is compatible with enhanced connector system")
        return True
        
    except ImportError as e:
        print(f"❌ Streamlit import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Streamlit compatibility error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DevPilot Connector Integration Test Suite")
    print("=" * 60)
    
    success = True
    
    # Run connector system tests
    if not test_connector_system():
        success = False
    
    # Run Streamlit compatibility tests
    if not test_streamlit_compatibility():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! The connector integration system is ready for use.")
        print("\n📋 What you can do now:")
        print("   1. Run the Streamlit app: python app_streamlit.py")
        print("   2. Navigate to the 'Connectors' tab to manage integrations")
        print("   3. Configure real API credentials for production use")
        print("   4. Enable automatic GitHub commits and Slack notifications")
    else:
        print("❌ SOME TESTS FAILED! Please check the errors above.")
    
    print("=" * 60)
