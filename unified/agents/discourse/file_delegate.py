"""
File delegation for discourse mode - read-only operations
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
from unified.tools.file_tools import ReadFileTool
from unified.tools.base import ToolContext


class DiscourseFileDelegate:
    """
    Handles read-only file operations for discourse mode.
    Ensures all file access is strictly read-only.
    """
    
    def __init__(self, working_dir: Optional[Path] = None):
        self.working_dir = working_dir or Path.cwd()
        self.read_tool = ReadFileTool()
        self.accessed_files = []  # Track accessed files for context
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Read a file in read-only mode.
        Records access for conversation context.
        """
        try:
            context = ToolContext(
                working_directory=self.working_dir,
                dry_run=False,
                sandbox=True  # Extra safety
            )
            
            result = self.read_tool.execute(context, file_path, encoding)
            
            if result.success:
                # Track access
                self.accessed_files.append({
                    'path': file_path,
                    'timestamp': result.end_time,
                    'size': len(result.output) if result.output else 0
                })
                
                return {
                    'status': 'success',
                    'content': result.output,
                    'path': file_path,
                    'encoding': encoding
                }
            else:
                return {
                    'status': 'error',
                    'message': result.error or 'Failed to read file',
                    'path': file_path
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'File read error: {str(e)}',
                'path': file_path
            }
    
    def search_files(self, pattern: str, directory: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for files matching a pattern (read-only).
        Uses glob patterns for file discovery.
        """
        try:
            search_dir = Path(directory) if directory else self.working_dir
            
            # Ensure we're within working directory
            if not search_dir.is_relative_to(self.working_dir):
                return {
                    'status': 'error',
                    'message': 'Search directory must be within working directory'
                }
            
            # Use glob for pattern matching
            matches = []
            for path in search_dir.rglob(pattern):
                if path.is_file():
                    matches.append({
                        'path': str(path),
                        'relative_path': str(path.relative_to(self.working_dir)),
                        'size': path.stat().st_size,
                        'modified': path.stat().st_mtime
                    })
            
            return {
                'status': 'success',
                'pattern': pattern,
                'directory': str(search_dir),
                'matches': matches[:50],  # Limit results
                'total_matches': len(matches)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Search error: {str(e)}',
                'pattern': pattern
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file metadata without reading content.
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {
                    'status': 'error',
                    'message': 'File does not exist',
                    'path': file_path
                }
            
            if not path.is_file():
                return {
                    'status': 'error',
                    'message': 'Path is not a file',
                    'path': file_path
                }
            
            stat = path.stat()
            
            return {
                'status': 'success',
                'path': file_path,
                'name': path.name,
                'extension': path.suffix,
                'size': stat.st_size,
                'size_human': self._format_size(stat.st_size),
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'is_text': self._is_likely_text(path),
                'parent_dir': str(path.parent)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'File info error: {str(e)}',
                'path': file_path
            }
    
    def list_directory(self, directory: Optional[str] = None) -> Dict[str, Any]:
        """
        List directory contents (read-only).
        """
        try:
            dir_path = Path(directory) if directory else self.working_dir
            
            if not dir_path.exists():
                return {
                    'status': 'error',
                    'message': 'Directory does not exist',
                    'path': str(dir_path)
                }
            
            if not dir_path.is_dir():
                return {
                    'status': 'error',
                    'message': 'Path is not a directory',
                    'path': str(dir_path)
                }
            
            contents = {
                'files': [],
                'directories': []
            }
            
            for item in dir_path.iterdir():
                if item.is_file():
                    contents['files'].append({
                        'name': item.name,
                        'size': item.stat().st_size,
                        'extension': item.suffix
                    })
                elif item.is_dir():
                    contents['directories'].append({
                        'name': item.name,
                        'item_count': len(list(item.iterdir()))
                    })
            
            return {
                'status': 'success',
                'path': str(dir_path),
                'contents': contents,
                'total_files': len(contents['files']),
                'total_directories': len(contents['directories'])
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Directory list error: {str(e)}',
                'path': directory or str(self.working_dir)
            }
    
    def get_accessed_files(self) -> List[Dict[str, Any]]:
        """Get list of files accessed during this session"""
        return self.accessed_files
    
    def clear_access_history(self):
        """Clear the file access history"""
        self.accessed_files = []
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _is_likely_text(self, path: Path) -> bool:
        """Guess if file is likely text based on extension"""
        text_extensions = {
            '.txt', '.md', '.py', '.js', '.ts', '.jsx', '.tsx',
            '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go',
            '.rs', '.rb', '.php', '.html', '.css', '.scss',
            '.json', '.xml', '.yaml', '.yml', '.toml', '.ini',
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat',
            '.sql', '.r', '.R', '.jl', '.lua', '.vim', '.el'
        }
        return path.suffix.lower() in text_extensions