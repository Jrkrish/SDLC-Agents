#!/usr/bin/env python3
"""
Alternative runner for DevPilot that skips Groq imports
"""

import os
import sys
sys.path.append('.')

# Monkey patch to skip groq imports
import builtins
real_import = builtins.__import__

def mock_import(name, *args, **kwargs):
    if 'groq' in name.lower():
        # Return a mock module for groq-related imports
        class MockModule:
            def __getattr__(self, name):
                return lambda *args, **kwargs: None
        return MockModule()
    return real_import(name, *args, **kwargs)

builtins.__import__ = mock_import

# Now run the streamlit app
import streamlit.web.cli as stcli

if __name__ == '__main__':
    sys.argv = ["streamlit", "run", "app_streamlit.py"]
    sys.exit(stcli.main())
