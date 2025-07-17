#!/usr/bin/env python3
"""
Command-line deployment tool for MCP Unified Agents
Usage: python deploy.py [command] [options]
"""
import sys
import os
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deployment import DeploymentManager


def main():
    parser = argparse.ArgumentParser(
        description='Deploy MCP Unified Agents from development to production',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python deploy.py status              # Check deployment status
  python deploy.py deploy              # Deploy changes
  python deploy.py deploy --dry-run    # Preview changes without deploying
  python deploy.py rollback            # Rollback to previous version
  python deploy.py rollback v0.1.0     # Rollback to specific version
        """
    )
    
    # Get paths from environment or use defaults
    default_dev = os.path.dirname(os.path.abspath(__file__))
    default_prod = os.path.expanduser("~/mcp-config/servers/mcp-unified-agents")
    
    parser.add_argument('command', choices=['status', 'deploy', 'rollback'],
                       help='Command to execute')
    parser.add_argument('version', nargs='?', default=None,
                       help='Version to rollback to (for rollback command)')
    parser.add_argument('--dev-path', default=os.environ.get('MCP_DEV_PATH', default_dev),
                       help=f'Development path (default: {default_dev})')
    parser.add_argument('--prod-path', default=os.environ.get('MCP_PROD_PATH', default_prod),
                       help=f'Production path (default: {default_prod})')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without deploying')
    
    args = parser.parse_args()
    
    # Initialize deployment manager
    try:
        dm = DeploymentManager(args.dev_path, args.prod_path)
    except Exception as e:
        print(f"❌ Failed to initialize deployment manager: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'status':
            # Show deployment status
            status = dm.get_status()
            
            print(f"📊 Deployment Status\n")
            print(f"Current version: {status['current_version']}")
            
            if status['last_deployment']:
                last = status['last_deployment']
                print(f"Last deployment: {last['deployed']} (v{last['version']})")
                print(f"Deployed from: {last['deployed_from']}")
                if last.get('git_commit'):
                    print(f"Git commit: {last['git_commit']}")
            
            if status['pending_changes']:
                print(f"\n📝 Pending Changes ({len(status['pending_changes'])} files)")
                for change in status['pending_changes']:
                    print(f"  - {change['file']} ({change['action']})")
            else:
                print("\n✅ No pending changes - production is up to date!")
            
            if status['is_locked']:
                lock_info = status['lock_info']
                print(f"\n⚠️  Deployment locked by: {lock_info['user']}@{lock_info['hostname']}")
                print(f"   Since: {lock_info['locked_at']}")
        
        elif args.command == 'deploy':
            # Deploy changes
            if args.dry_run:
                print("🔍 Deployment Preview (Dry Run)\n")
            else:
                print("🚀 Starting deployment...\n")
            
            result = dm.deploy(dry_run=args.dry_run)
            
            if result['success']:
                if result.get('message'):
                    print(result['message'])
                elif args.dry_run:
                    print(f"Files to update: {len(result['files_updated'])}")
                    for file in result['files_updated']:
                        print(f"  - {file}")
                    print("\nRun without --dry-run to apply these changes.")
                else:
                    print(f"✅ Deployment successful!")
                    print(f"Version: {result['version']}")
                    print(f"Files updated: {len(result['files_updated'])}")
                    for file in result['files_updated']:
                        print(f"  ✓ {file}")
            else:
                print(f"❌ Deployment failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
        
        elif args.command == 'rollback':
            # Rollback deployment
            from pathlib import Path
            backup_dir = Path(dm.backup_dir)
            backups = sorted(backup_dir.glob("v*_*"), reverse=True)
            
            if not backups:
                print("❌ No backups available for rollback")
                sys.exit(1)
            
            if args.version:
                # Find specific version
                backup_path = None
                for backup in backups:
                    if backup.name.startswith(f"v{args.version}_"):
                        backup_path = backup
                        break
                if not backup_path:
                    print(f"❌ No backup found for version {args.version}")
                    print("\nAvailable versions:")
                    for backup in backups[:10]:  # Show last 10
                        version = backup.name.split('_')[0]
                        print(f"  - {version}")
                    sys.exit(1)
            else:
                # Use most recent backup
                backup_path = backups[0]
                version = backup_path.name.split('_')[0][1:]
                print(f"Rolling back to version {version}...")
            
            # Perform rollback
            dm.rollback(backup_path)
            print(f"✅ Rollback successful!")
            print(f"Restored to: {backup_path.name}")
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()