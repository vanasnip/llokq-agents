"""
Unit tests for git commit functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from unified.tools.git_tools import GitCommitAnalyzer
from unified.tools.base import ToolContext


class TestGitCommitAnalyzer:
    """Test GitCommitAnalyzer functionality"""
    
    def setup_method(self):
        """Set up test instance"""
        self.analyzer = GitCommitAnalyzer()
        self.context = ToolContext(working_directory=Path("/test"))
    
    def test_protected_branches_defined(self):
        """Test that protected branches are properly defined"""
        assert "main" in GitCommitAnalyzer.PROTECTED_BRANCHES
        assert "dev" in GitCommitAnalyzer.PROTECTED_BRANCHES
        assert "staging" in GitCommitAnalyzer.PROTECTED_BRANCHES
        assert "master" in GitCommitAnalyzer.PROTECTED_BRANCHES
    
    @patch('subprocess.run')
    def test_is_git_repo(self, mock_run):
        """Test git repository detection"""
        # Test positive case
        mock_run.return_value = MagicMock(returncode=0)
        assert self.analyzer._is_git_repo() is True
        
        # Test negative case
        mock_run.side_effect = Exception()
        assert self.analyzer._is_git_repo() is False
    
    @patch('subprocess.run')
    def test_get_current_branch(self, mock_run):
        """Test getting current branch"""
        mock_run.return_value = MagicMock(
            returncode=0, 
            stdout="feature/test-branch\n"
        )
        assert self.analyzer._get_current_branch() == "feature/test-branch"
    
    def test_suggest_branch_name(self):
        """Test branch name generation"""
        # Test with test files
        files = [
            {'path': 'tests/test_auth.py', 'status': 'M'},
            {'path': 'tests/test_user.py', 'status': 'M'}
        ]
        branch = self.analyzer._suggest_branch_name(files)
        assert branch.startswith('test/')
        
        # Test with docs
        files = [
            {'path': 'README.md', 'status': 'M'},
            {'path': 'docs/api.md', 'status': 'M'}
        ]
        branch = self.analyzer._suggest_branch_name(files)
        assert branch.startswith('docs/')
        
        # Test with feature files
        files = [
            {'path': 'src/auth.py', 'status': 'A'},
            {'path': 'src/user.py', 'status': 'A'}
        ]
        branch = self.analyzer._suggest_branch_name(files)
        assert branch.startswith('feature/') or branch.startswith('fix/')
    
    def test_group_changes_single_commit(self):
        """Test grouping changes with single commit flag"""
        files = [
            {'path': 'src/auth.py', 'status': 'M'},
            {'path': 'tests/test_auth.py', 'status': 'M'},
            {'path': 'README.md', 'status': 'M'}
        ]
        
        groups = self.analyzer._group_changes(files, single_commit=True)
        assert len(groups) == 1
        assert len(groups[0]['files']) == 3
    
    def test_group_changes_multiple_commits(self):
        """Test grouping changes into multiple commits"""
        files = [
            {'path': 'src/auth.py', 'status': 'M'},
            {'path': 'tests/test_auth.py', 'status': 'M'},
            {'path': 'README.md', 'status': 'M'}
        ]
        
        groups = self.analyzer._group_changes(files, single_commit=False)
        assert len(groups) >= 2  # At least src and tests/docs separated
        
        # Check that test files are grouped together
        test_group = next((g for g in groups if g['type'] == 'test'), None)
        if test_group:
            assert all('test' in f['path'] for f in test_group['files'])
    
    def test_determine_commit_type(self):
        """Test commit type determination"""
        # Test files
        test_files = [{'path': 'tests/test_auth.py', 'status': 'M'}]
        assert self.analyzer._determine_commit_type(test_files) == 'test'
        
        # Doc files
        doc_files = [{'path': 'README.md', 'status': 'M'}]
        assert self.analyzer._determine_commit_type(doc_files) == 'docs'
        
        # New feature files
        feat_files = [{'path': 'src/new_feature.py', 'status': 'A'}]
        assert self.analyzer._determine_commit_type(feat_files) == 'feat'
        
        # Modified files (fixes)
        fix_files = [{'path': 'src/auth.py', 'status': 'M'}]
        assert self.analyzer._determine_commit_type(fix_files) == 'fix'
    
    def test_should_prompt_for_pr(self):
        """Test PR prompt logic"""
        # Should prompt - normal case
        analysis = {
            'current_branch': 'feature/test',
            'on_protected_branch': False,
            'commit_results': [{'success': True}]
        }
        options = {'dry_run': False, 'skip_safety': False}
        assert self.analyzer._should_prompt_for_pr(analysis, options) is True
        
        # Should not prompt - dry run
        options['dry_run'] = True
        assert self.analyzer._should_prompt_for_pr(analysis, options) is False
        
        # Should not prompt - skip safety
        options = {'dry_run': False, 'skip_safety': True}
        assert self.analyzer._should_prompt_for_pr(analysis, options) is False
        
        # Should not prompt - on protected branch
        analysis['current_branch'] = 'main'
        analysis['on_protected_branch'] = True
        options = {'dry_run': False, 'skip_safety': False}
        assert self.analyzer._should_prompt_for_pr(analysis, options) is False
        
        # Should not prompt - failed commits
        analysis = {
            'current_branch': 'feature/test',
            'commit_results': [{'success': False}]
        }
        assert self.analyzer._should_prompt_for_pr(analysis, options) is False
    
    @patch('subprocess.run')
    def test_analyze_changes_on_protected_branch(self, mock_run):
        """Test analysis when on protected branch"""
        # Mock current branch as 'main'
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="main\n"),  # Current branch
            MagicMock(returncode=0, stdout="M\tsrc/file.py\n"),  # Staged files
        ]
        
        analysis = self.analyzer._analyze_changes({'all': False})
        
        assert analysis['current_branch'] == 'main'
        assert analysis['on_protected_branch'] is True
        assert analysis['suggested_branch'] != ""
        assert len(analysis['changed_files']) > 0
    
    def test_validate_input_not_git_repo(self):
        """Test validation when not in git repo"""
        with patch.object(self.analyzer, '_is_git_repo', return_value=False):
            errors = self.analyzer.validate_input({})
            assert len(errors) > 0
            assert "Not in a git repository" in errors[0]
    
    def test_dry_run_preview(self):
        """Test dry run preview generation"""
        with patch.object(self.analyzer, '_analyze_changes') as mock_analyze:
            mock_analyze.return_value = {
                'on_protected_branch': True,
                'suggested_branch': 'fix/auth-bug',
                'commit_groups': [
                    {'type': 'fix', 'scope': 'auth', 'description': 'fix login bug'},
                    {'type': 'test', 'scope': None, 'description': 'add tests'}
                ]
            }
            
            preview = self.analyzer.dry_run(self.context, {'skip_safety': False})
            assert "Would create feature branch: fix/auth-bug" in preview
            assert "2 commits" in preview