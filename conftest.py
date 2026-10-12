import os
import sys

# Add the project root directory to sys.path so pytest can locate main.py
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))