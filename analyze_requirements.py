#!/usr/bin/env python3
"""
Analyze Portfolio Management System Requirements using AI Team BA Agent

This script uses the BA Agent from the aiteam project to analyze
the user requirements for the Personal Portfolio Management System.

Usage:
    python3 analyze_requirements.py <requirements_file>
    python3 analyze_requirements.py requirements/user_requirement.md
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add aiteam to Python path
aiteam_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aiteam')
sys.path.insert(0, aiteam_path)

from agents.ba_agent import BAAgent

def main(requirements_file=None):
    """Analyze the PPS requirements using BA Agent"""
    
    print("="*70)
    print("📊 Personal Portfolio Management System - Requirements Analysis")
    print("="*70)
    print()
    
    # Load environment variables from aiteam
    env_path = os.path.join(aiteam_path, '.env')
    load_dotenv(env_path, override=True)
    
    # Configure LLM - Default to GitHub Models API (GPT-4o)
    llm_config = {
        'provider': os.getenv('LLM_PROVIDER', 'github_copilot_cli'),
        'model': os.getenv('GITHUB_MODEL', 'gpt-4o')
    }
    
    # Configure JIRA (optional for this use case)
    jira_config = {
        'server': os.getenv('JIRA_SERVER', 'https://example.atlassian.net'),
        'user': os.getenv('JIRA_USER', 'user@example.com'),
        'token': os.getenv('JIRA_API_TOKEN', 'token')
    }
    
    print("🤖 Initializing BA Agent...")
    print(f"   LLM Provider: {llm_config['provider']}")
    print(f"   Model: {llm_config['model']}")
    print()
    
    # Initialize BA Agent
    ba = BAAgent(llm_config, jira_config)
    
    # Use provided file or default
    if requirements_file is None:
        requirements_file = 'requirements/user_requirement.md'
    
    # Check if file exists
    if not os.path.exists(requirements_file):
        print(f"❌ Error: Requirements file not found: {requirements_file}")
        print(f"   Current directory: {os.getcwd()}")
        return 1
    
    print(f"📄 Reading requirements from: {requirements_file}")
    requirement_data = ba.read_requirement_file(requirements_file)
    
    if 'error' in requirement_data:
        print(f"❌ Error: {requirement_data['error']}")
        return 1
    
    print("✅ Requirements file loaded successfully")
    print()
    
    # Analyze requirements with AI
    print("🧠 Analyzing requirements with AI...")
    print("   This may take a few moments...")
    print()
    
    output_dir = 'requirements/analysis'
    analysis_result = ba.analyze_requirements(requirement_data, output_dir=output_dir)
    
    # Display results
    print()
    print("="*70)
    print("📋 Analysis Complete!")
    print("="*70)
    print()
    
    print("📂 Generated Files:")
    print(f"   • {output_dir}/requirements_analysis.md")
    print(f"   • {output_dir}/requirements.feature")
    print(f"   • {output_dir}/requirements_structured.json")
    print()
    
    print("📊 Analysis Summary:")
    print(f"   • Assumptions identified: {len(analysis_result.get('assumptions', []))}")
    print(f"   • User stories extracted: {len(analysis_result.get('user_stories', []))}")
    print()
    
    if analysis_result.get('assumptions'):
        print("💡 Key Assumptions:")
        for i, assumption in enumerate(analysis_result['assumptions'][:5], 1):
            print(f"   {i}. {assumption}")
        print()
    
    if analysis_result.get('user_stories'):
        print("👥 User Stories:")
        for i, story in enumerate(analysis_result['user_stories'][:5], 1):
            print(f"   {i}. {story['story'][:80]}...")
        print()
    
    print("="*70)
    print("✅ Analysis completed successfully!")
    print("="*70)
    print()
    print("📖 Next Steps:")
    print("   1. Review the analysis document:")
    print(f"      open {output_dir}/requirements_analysis.md")
    print()
    print("   2. Review the BDD scenarios:")
    print(f"      open {output_dir}/requirements.feature")
    print()
    print("   3. Use the structured data for implementation:")
    print(f"      cat {output_dir}/requirements_structured.json")
    print()
    
    return 0

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Analyze requirements using AI Team BA Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze default requirements file
  python3 analyze_requirements.py
  
  # Analyze specific requirements file
  python3 analyze_requirements.py requirements/user_requirement.md
  
  # Analyze from different location
  python3 analyze_requirements.py /path/to/requirements.md
        """
    )
    
    parser.add_argument(
        'requirements_file',
        nargs='?',
        default=None,
        help='Path to requirements file (default: requirements/user_requirement.md)'
    )
    
    args = parser.parse_args()
    
    try:
        sys.exit(main(args.requirements_file))
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
