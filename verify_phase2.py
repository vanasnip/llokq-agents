#!/usr/bin/env python3
"""Verify Phase 2 implementation without full imports"""

import ast
import os

def verify_file_contains(filepath, content):
    """Check if file contains specific content"""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return content in f.read()
    return False

# Test 1: Check discourse category in schema
print("✓ Checking AgentCategory enum...")
schema_has_discourse = verify_file_contains(
    "unified/agents/schema.py", 
    'DISCOURSE = "discourse"'
)
print(f"  - DISCOURSE category exists: {schema_has_discourse}")

# Test 2: Check discourse agent in config
print("\n✓ Checking discourse agent configuration...")
config_has_discourse = verify_file_contains(
    "unified/config/agents.yml",
    "discourse:"
)
print(f"  - Discourse agent in config: {config_has_discourse}")

# Test 3: Check CommandExecutor imports
print("\n✓ Checking CommandExecutor modifications...")
executor_has_import = verify_file_contains(
    "unified/core/command_executor.py",
    "from unified.agents.discourse import DiscourseContext, discourse_safe"
)
executor_has_mode = verify_file_contains(
    "unified/core/command_executor.py",
    "discourse_mode: bool = False"
)
executor_has_decorators = verify_file_contains(
    "unified/core/command_executor.py",
    "@discourse_safe()"
)
executor_has_mutates = verify_file_contains(
    "unified/core/command_executor.py",
    "CommandExecutor._execute_code._mutates = True"
)
print(f"  - Has discourse imports: {executor_has_import}")
print(f"  - Has discourse_mode parameter: {executor_has_mode}")
print(f"  - Has @discourse_safe decorators: {executor_has_decorators}")
print(f"  - Marks mutating methods: {executor_has_mutates}")

# Test 4: Check CLI modifications
print("\n✓ Checking CLI discourse support...")
cli_has_check = verify_file_contains(
    "unified/cli.py",
    "discourse_mode = any(a.name == 'discourse' for a in agents)"
)
print(f"  - CLI checks for discourse agent: {cli_has_check}")

# Test 5: Check discourse files exist
print("\n✓ Checking discourse module files...")
files_exist = all(os.path.exists(f) for f in [
    "unified/agents/discourse/__init__.py",
    "unified/agents/discourse/context.py",
    "unified/agents/discourse/agent.py",
    "tests/unit/test_discourse.py",
    "tests/integration/test_discourse_cli.py"
])
print(f"  - All discourse files exist: {files_exist}")

# Summary
all_checks = [
    schema_has_discourse,
    config_has_discourse,
    executor_has_import,
    executor_has_mode,
    executor_has_decorators,
    executor_has_mutates,
    cli_has_check,
    files_exist
]

print("\n" + "="*50)
if all(all_checks):
    print("✅ Phase 2 implementation VERIFIED!")
    print("All components are in place for discourse mode.")
else:
    print("❌ Some checks failed!")
    print(f"Passed: {sum(all_checks)}/{len(all_checks)}")