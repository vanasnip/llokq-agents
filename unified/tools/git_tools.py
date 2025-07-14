"""
Git tools for intelligent commit analysis and branch safety
"""
import subprocess
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from unified.tools.base import Tool, ToolContext, ToolCategory
import os


class GitCommitAnalyzer(Tool[Dict[str, Any]]):
    """Analyzes git changes and creates intelligent commits with branch safety"""
    
    PROTECTED_BRANCHES = ["main", "dev", "staging", "master"]
    
    def __init__(self):
        super().__init__(
            name="git_commit_analyzer",
            category=ToolCategory.ANALYSIS,
            description="Analyzes git changes and creates commits with branch safety"
        )
    
    def validate_input(self, options: Dict[str, Any]) -> List[str]:
        """Validate git commit options"""
        errors = []
        
        # Check if we're in a git repository
        if not self._is_git_repo():
            errors.append("Not in a git repository")
        
        return errors
    
    def dry_run(self, context: ToolContext, options: Dict[str, Any]) -> str:
        """Preview what commits would be created"""
        analysis = self._analyze_changes(options)
        
        if analysis['on_protected_branch'] and not options.get('skip_safety', False):
            return f"Would create feature branch: {analysis['suggested_branch']}\nThen create {len(analysis['commit_groups'])} commits"
        
        return f"Would create {len(analysis['commit_groups'])} commits"
    
    def _execute_impl(self, context: ToolContext, options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute git commit analysis and creation"""
        # Analyze current state
        analysis = self._analyze_changes(options)
        
        # Handle protected branch
        if analysis['on_protected_branch'] and not options.get('skip_safety', False):
            if not options.get('dry_run', False):
                branch_result = self._create_feature_branch(analysis['suggested_branch'])
                if not branch_result['success']:
                    return branch_result
                analysis['created_branch'] = branch_result['branch_name']
        
        # Create commits if not dry run
        if not options.get('dry_run', False):
            commit_results = self._create_commits(analysis['commit_groups'], options)
            analysis['commit_results'] = commit_results
            
            # Check if we should prompt for PR
            should_prompt_pr = self._should_prompt_for_pr(analysis, options)
            analysis['should_prompt_pr'] = should_prompt_pr
        
        return analysis
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        try:
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                         capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _get_current_branch(self) -> str:
        """Get current git branch name"""
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""
    
    def _analyze_changes(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze git changes and group them"""
        current_branch = self._get_current_branch()
        on_protected = current_branch in self.PROTECTED_BRANCHES
        
        # Get changed files
        changed_files = self._get_changed_files(options.get('all', False))
        
        # Analyze changes for branch naming
        suggested_branch = ""
        if on_protected:
            suggested_branch = self._suggest_branch_name(changed_files)
        
        # Group changes into logical commits
        commit_groups = self._group_changes(changed_files, options.get('single', False))
        
        return {
            'current_branch': current_branch,
            'on_protected_branch': on_protected,
            'suggested_branch': suggested_branch,
            'changed_files': changed_files,
            'commit_groups': commit_groups
        }
    
    def _get_changed_files(self, include_all: bool) -> List[Dict[str, Any]]:
        """Get list of changed files with their status"""
        files = []
        
        # Get staged files
        staged_result = subprocess.run(['git', 'diff', '--cached', '--name-status'],
                                     capture_output=True, text=True)
        for line in staged_result.stdout.strip().split('\n'):
            if line:
                status, filepath = line.split('\t', 1)
                files.append({
                    'path': filepath,
                    'status': status,
                    'staged': True
                })
        
        if include_all:
            # Get unstaged files
            unstaged_result = subprocess.run(['git', 'diff', '--name-status'],
                                           capture_output=True, text=True)
            for line in unstaged_result.stdout.strip().split('\n'):
                if line:
                    status, filepath = line.split('\t', 1)
                    files.append({
                        'path': filepath,
                        'status': status,
                        'staged': False
                    })
            
            # Get untracked files
            untracked_result = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'],
                                            capture_output=True, text=True)
            for filepath in untracked_result.stdout.strip().split('\n'):
                if filepath:
                    files.append({
                        'path': filepath,
                        'status': 'A',
                        'staged': False
                    })
        
        return files
    
    def _suggest_branch_name(self, files: List[Dict[str, Any]]) -> str:
        """Suggest a branch name based on changed files"""
        if not files:
            return "feature/updates"
        
        # Analyze file paths and changes
        paths = [f['path'] for f in files]
        
        # Determine branch type
        branch_type = "feature"
        if any('test' in p or 'spec' in p for p in paths):
            branch_type = "test"
        elif any(p.endswith('.md') or 'README' in p or 'docs/' in p for p in paths):
            branch_type = "docs"
        elif self._analyze_diff_for_fixes():
            branch_type = "fix"
        
        # Generate description
        description = self._generate_branch_description(paths)
        
        # Sanitize branch name
        branch_name = f"{branch_type}/{description}"
        branch_name = re.sub(r'[^a-zA-Z0-9/_-]', '-', branch_name)
        branch_name = re.sub(r'-+', '-', branch_name).strip('-')
        
        # Limit length
        if len(branch_name) > 50:
            branch_name = branch_name[:50].rstrip('-')
        
        return branch_name
    
    def _analyze_diff_for_fixes(self) -> bool:
        """Check if changes look like bug fixes"""
        try:
            diff_result = subprocess.run(['git', 'diff', '--cached'],
                                       capture_output=True, text=True)
            diff_content = diff_result.stdout.lower()
            fix_keywords = ['fix', 'bug', 'error', 'issue', 'resolve', 'correct']
            return any(keyword in diff_content for keyword in fix_keywords)
        except:
            return False
    
    def _generate_branch_description(self, paths: List[str]) -> str:
        """Generate branch description from file paths"""
        if not paths:
            return "updates"
        
        # Look for common patterns
        if any('analytics' in p for p in paths):
            return "analytics-improvements"
        elif any('voice' in p or 'speech' in p for p in paths):
            return "voice-input-enhancement"
        elif any('component' in p for p in paths):
            return "ui-component-updates"
        elif any('store' in p or 'state' in p for p in paths):
            return "state-management"
        
        # Use first directory
        first_dir = paths[0].split('/')[0]
        return f"{first_dir}-updates"
    
    def _create_feature_branch(self, branch_name: str) -> Dict[str, Any]:
        """Create and switch to feature branch"""
        try:
            # Fetch latest
            subprocess.run(['git', 'fetch', 'origin', 'dev'], 
                         capture_output=True, check=True)
            
            # Create and checkout branch
            subprocess.run(['git', 'checkout', '-b', branch_name, 'origin/dev'],
                         capture_output=True, check=True)
            
            return {
                'success': True,
                'branch_name': branch_name,
                'message': f'Created and switched to branch: {branch_name}'
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': f'Failed to create branch: {e.stderr.decode() if e.stderr else str(e)}'
            }
    
    def _group_changes(self, files: List[Dict[str, Any]], single_commit: bool) -> List[Dict[str, Any]]:
        """Group changes into logical commits"""
        if single_commit or len(files) <= 1:
            return [{
                'files': files,
                'type': 'feat',
                'scope': None,
                'description': 'Update files'
            }]
        
        groups = []
        
        # Group by feature area
        file_groups = {}
        for file in files:
            path = file['path']
            
            # Determine group key
            if 'test' in path or 'spec' in path:
                key = 'tests'
            elif path.endswith('.md') or 'docs/' in path:
                key = 'docs'
            elif '/' in path:
                # Group by top-level directory
                key = path.split('/')[0]
            else:
                key = 'root'
            
            if key not in file_groups:
                file_groups[key] = []
            file_groups[key].append(file)
        
        # Create commit groups
        for key, group_files in file_groups.items():
            commit_type = self._determine_commit_type(group_files)
            groups.append({
                'files': group_files,
                'type': commit_type,
                'scope': key if key not in ['tests', 'docs', 'root'] else None,
                'description': self._generate_commit_description(group_files, key)
            })
        
        return groups
    
    def _determine_commit_type(self, files: List[Dict[str, Any]]) -> str:
        """Determine conventional commit type"""
        paths = [f['path'] for f in files]
        
        if all('test' in p or 'spec' in p for p in paths):
            return 'test'
        elif all(p.endswith('.md') or 'docs/' in p for p in paths):
            return 'docs'
        elif any(f['status'] == 'A' for f in files):
            return 'feat'
        else:
            return 'fix'
    
    def _generate_commit_description(self, files: List[Dict[str, Any]], group_key: str) -> str:
        """Generate commit description"""
        if group_key == 'tests':
            return 'add tests'
        elif group_key == 'docs':
            return 'update documentation'
        elif len(files) == 1:
            filename = Path(files[0]['path']).name
            return f'update {filename}'
        else:
            return f'update {group_key} files'
    
    def _create_commits(self, commit_groups: List[Dict[str, Any]], options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create the actual commits"""
        results = []
        
        for group in commit_groups:
            # Stage files if needed
            for file in group['files']:
                if not file['staged']:
                    subprocess.run(['git', 'add', file['path']], capture_output=True)
            
            # Build commit message
            message = f"{group['type']}"
            if group['scope']:
                message += f"({group['scope']})"
            message += f": {group['description']}"
            
            # Create commit
            try:
                subprocess.run(['git', 'commit', '-m', message], 
                             capture_output=True, check=True)
                results.append({
                    'success': True,
                    'message': message
                })
            except subprocess.CalledProcessError as e:
                results.append({
                    'success': False,
                    'message': message,
                    'error': str(e)
                })
        
        return results
    
    def _should_prompt_for_pr(self, analysis: Dict[str, Any], options: Dict[str, Any]) -> bool:
        """Determine if we should prompt for PR creation"""
        # Don't prompt on dry run
        if options.get('dry_run', False):
            return False
        
        # Don't prompt if skip_safety was used
        if options.get('skip_safety', False):
            return False
        
        # Don't prompt if no commits were created
        if 'commit_results' not in analysis:
            return False
        
        # Don't prompt if any commits failed
        if any(not r['success'] for r in analysis['commit_results']):
            return False
        
        # Don't prompt on protected branches (unless we created a feature branch)
        current_branch = analysis.get('created_branch', analysis['current_branch'])
        if current_branch in self.PROTECTED_BRANCHES:
            return False
        
        return True