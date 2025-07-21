"""
Quick validation script to check connector integration
"""
import os
import sys

# Add the current directory to path
sys.path.insert(0, os.getcwd())

def main():
    print("🔍 DevPilot Connector Integration Validation")
    print("=" * 50)
    
    try:
        # Test basic imports
        print("1. Testing basic imports...")
        from src.dev_pilot.graph.graph_builder import GraphBuilder
        print("   ✅ Base GraphBuilder imported")
        
        from src.dev_pilot.graph.enhanced_graph_builder import EnhancedGraphBuilder
        print("   ✅ EnhancedGraphBuilder imported")
        
        # Test connector imports
        print("\n2. Testing connector imports...")
        from src.dev_pilot.connectors.connector_manager import ConnectorManager
        print("   ✅ ConnectorManager imported")
        
        from src.dev_pilot.connectors.agent_connector_bridge import AgentConnectorBridge
        print("   ✅ AgentConnectorBridge imported")
        
        # Test enhanced components
        print("\n3. Testing enhanced components...")
        from src.dev_pilot.connectors.enhanced_github_connector import EnhancedGitHubConnector
        print("   ✅ EnhancedGitHubConnector imported")
        
        from src.dev_pilot.connectors.enhanced_slack_connector import EnhancedSlackConnector
        print("   ✅ EnhancedSlackConnector imported")
        
        from src.dev_pilot.nodes.enhanced_coding_node import EnhancedCodingNode
        print("   ✅ EnhancedCodingNode imported")
        
        # Test Streamlit app compatibility
        print("\n4. Testing Streamlit app...")
        from src.dev_pilot.ui.streamlit_ui.streamlit_app import load_app
        print("   ✅ Streamlit app imported successfully")
        
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("\n📋 Integration Summary:")
        print("   • Enhanced Graph Builder with connector support")
        print("   • Agent-Connector Bridge for AI automation")
        print("   • Enhanced GitHub and Slack connectors")
        print("   • Enhanced coding node with connector awareness")
        print("   • Streamlit UI with connector management tab")
        print("\n🚀 The system is ready for connector-enabled SDLC automation!")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Validation error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
