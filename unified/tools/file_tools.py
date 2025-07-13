"""
File system tools with safety validation
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional, Union
from unified.tools.base import Tool, ToolContext, ToolCategory, ToolResult
import hashlib
import json
from datetime import datetime


class ReadFileTool(Tool[str]):
    """Safe file reading tool"""
    
    def __init__(self):
        super().__init__(
            name="read_file",
            category=ToolCategory.FILE_SYSTEM,
            description="Safely read text files with encoding detection"
        )
    
    def validate_input(self, file_path: Union[str, Path], encoding: str = "utf-8") -> List[str]:
        """Validate file reading parameters"""
        errors = []
        
        if not file_path:
            errors.append("File path is required")
            return errors
        
        path = Path(file_path)
        
        if not path.exists():
            errors.append(f"File does not exist: {path}")
        elif not path.is_file():
            errors.append(f"Path is not a file: {path}")
        elif not os.access(path, os.R_OK):
            errors.append(f"File is not readable: {path}")
        
        # Check file size (prevent reading huge files)
        if path.exists() and path.stat().st_size > 10 * 1024 * 1024:  # 10MB
            errors.append(f"File too large (>10MB): {path}")
        
        # Validate encoding
        valid_encodings = ['utf-8', 'utf-16', 'ascii', 'latin-1']
        if encoding not in valid_encodings:
            errors.append(f"Invalid encoding: {encoding}. Must be one of {valid_encodings}")
        
        return errors
    
    def dry_run(self, context: ToolContext, file_path: Union[str, Path], encoding: str = "utf-8") -> str:
        """Preview what would be read"""
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            return f"Would read file: {path} ({size} bytes, encoding: {encoding})"
        return f"Would attempt to read non-existent file: {path}"
    
    def _execute_impl(self, context: ToolContext, file_path: Union[str, Path], encoding: str = "utf-8") -> str:
        """Read file contents"""
        path = Path(file_path)
        
        # Ensure we're within working directory if specified
        if context.working_directory:
            abs_path = path if path.is_absolute() else context.working_directory / path
            if not abs_path.resolve().is_relative_to(context.working_directory.resolve()):
                raise ValueError(f"File path {abs_path} is outside working directory")
            path = abs_path
        
        with open(path, 'r', encoding=encoding) as f:
            return f.read()


class WriteFileTool(Tool[None]):
    """Safe file writing tool with backup support"""
    
    def __init__(self):
        super().__init__(
            name="write_file",
            category=ToolCategory.FILE_SYSTEM,
            description="Safely write files with automatic backup"
        )
        self.backup_enabled = True
    
    def validate_input(self, file_path: Union[str, Path], content: str, 
                      encoding: str = "utf-8", create_dirs: bool = False) -> List[str]:
        """Validate file writing parameters"""
        errors = []
        
        if not file_path:
            errors.append("File path is required")
            return errors
        
        if content is None:
            errors.append("Content is required")
        
        path = Path(file_path)
        
        # Check parent directory
        if not path.parent.exists() and not create_dirs:
            errors.append(f"Parent directory does not exist: {path.parent}")
        
        # Check if file exists and is writable
        if path.exists() and not os.access(path, os.W_OK):
            errors.append(f"File is not writable: {path}")
        
        # Check directory permissions
        check_dir = path.parent if path.parent.exists() else path.parent.parent
        if check_dir.exists() and not os.access(check_dir, os.W_OK):
            errors.append(f"Directory is not writable: {check_dir}")
        
        return errors
    
    def dry_run(self, context: ToolContext, file_path: Union[str, Path], content: str,
                encoding: str = "utf-8", create_dirs: bool = False) -> str:
        """Preview what would be written"""
        path = Path(file_path)
        size = len(content.encode(encoding))
        
        actions = []
        if create_dirs and not path.parent.exists():
            actions.append(f"Create directory: {path.parent}")
        
        if path.exists():
            if self.backup_enabled:
                actions.append(f"Backup existing file to: {path}.backup")
            actions.append(f"Overwrite file: {path} ({size} bytes)")
        else:
            actions.append(f"Create new file: {path} ({size} bytes)")
        
        return " → ".join(actions)
    
    def _execute_impl(self, context: ToolContext, file_path: Union[str, Path], content: str,
                     encoding: str = "utf-8", create_dirs: bool = False) -> None:
        """Write file with safety checks"""
        path = Path(file_path)
        
        # Ensure we're within working directory
        if context.working_directory:
            abs_path = path if path.is_absolute() else context.working_directory / path
            if not abs_path.resolve().is_relative_to(context.working_directory.resolve()):
                raise ValueError(f"File path {abs_path} is outside working directory")
            path = abs_path
        
        # Create directories if needed
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing file
        if path.exists() and self.backup_enabled:
            backup_path = path.with_suffix(path.suffix + '.backup')
            shutil.copy2(path, backup_path)
        
        # Write file
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)


class DeleteFileTool(Tool[None]):
    """Safe file deletion tool"""
    
    def __init__(self):
        super().__init__(
            name="delete_file",
            category=ToolCategory.FILE_SYSTEM,
            description="Safely delete files with optional trash support"
        )
        self.use_trash = True
    
    def validate_input(self, file_path: Union[str, Path], force: bool = False) -> List[str]:
        """Validate deletion parameters"""
        errors = []
        
        if not file_path:
            errors.append("File path is required")
            return errors
        
        path = Path(file_path)
        
        if not path.exists():
            if not force:
                errors.append(f"File does not exist: {path}")
        elif not path.is_file():
            errors.append(f"Path is not a file: {path}")
        elif not os.access(path.parent, os.W_OK):
            errors.append(f"No write permission in parent directory: {path.parent}")
        
        # Prevent deletion of critical files
        critical_patterns = ['.git', '.env', 'node_modules', '__pycache__']
        for pattern in critical_patterns:
            if pattern in str(path):
                errors.append(f"Cannot delete files in {pattern} directories")
        
        return errors
    
    def dry_run(self, context: ToolContext, file_path: Union[str, Path], force: bool = False) -> str:
        """Preview deletion"""
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            action = "Move to trash" if self.use_trash else "Permanently delete"
            return f"{action}: {path} ({size} bytes)"
        return f"File does not exist (no action needed): {path}"
    
    def _execute_impl(self, context: ToolContext, file_path: Union[str, Path], force: bool = False) -> None:
        """Delete file safely"""
        path = Path(file_path)
        
        # Ensure we're within working directory
        if context.working_directory:
            abs_path = path if path.is_absolute() else context.working_directory / path
            if not abs_path.resolve().is_relative_to(context.working_directory.resolve()):
                raise ValueError(f"File path {abs_path} is outside working directory")
            path = abs_path
        
        if not path.exists():
            if force:
                return  # Nothing to do
            raise FileNotFoundError(f"File not found: {path}")
        
        if self.use_trash:
            # Move to trash directory
            trash_dir = context.working_directory / '.trash' if context.working_directory else Path.home() / '.trash'
            trash_dir.mkdir(exist_ok=True)
            
            # Create unique name in trash
            trash_name = f"{path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            trash_path = trash_dir / trash_name
            
            shutil.move(str(path), str(trash_path))
        else:
            # Permanent deletion
            path.unlink()


class FileSearchTool(Tool[List[Path]]):
    """Search for files matching patterns"""
    
    def __init__(self):
        super().__init__(
            name="file_search",
            category=ToolCategory.FILE_SYSTEM,
            description="Search for files by name, content, or attributes"
        )
    
    def validate_input(self, pattern: str, search_type: str = "name", 
                      case_sensitive: bool = False, max_results: int = 100) -> List[str]:
        """Validate search parameters"""
        errors = []
        
        if not pattern:
            errors.append("Search pattern is required")
        
        valid_types = ['name', 'content', 'extension']
        if search_type not in valid_types:
            errors.append(f"Invalid search type: {search_type}. Must be one of {valid_types}")
        
        if max_results < 1 or max_results > 10000:
            errors.append("max_results must be between 1 and 10000")
        
        return errors
    
    def dry_run(self, context: ToolContext, pattern: str, search_type: str = "name",
                case_sensitive: bool = False, max_results: int = 100) -> str:
        """Preview search operation"""
        search_dir = context.working_directory or Path.cwd()
        case_str = "case-sensitive" if case_sensitive else "case-insensitive"
        return f"Would search for files in {search_dir} matching '{pattern}' ({search_type}, {case_str}, max {max_results} results)"
    
    def _execute_impl(self, context: ToolContext, pattern: str, search_type: str = "name",
                     case_sensitive: bool = False, max_results: int = 100) -> List[Path]:
        """Search for files"""
        search_dir = context.working_directory or Path.cwd()
        results = []
        
        # Convert pattern to lowercase if case-insensitive
        if not case_sensitive:
            pattern = pattern.lower()
        
        # Search based on type
        for path in search_dir.rglob('*'):
            if len(results) >= max_results:
                break
            
            if not path.is_file():
                continue
            
            try:
                if search_type == 'name':
                    name = path.name if case_sensitive else path.name.lower()
                    if pattern in name:
                        results.append(path)
                
                elif search_type == 'extension':
                    ext = path.suffix[1:] if path.suffix else ''
                    if not case_sensitive:
                        ext = ext.lower()
                    if pattern == ext:
                        results.append(path)
                
                elif search_type == 'content':
                    # Only search text files under 1MB
                    if path.stat().st_size > 1024 * 1024:
                        continue
                    
                    try:
                        content = path.read_text()
                        if not case_sensitive:
                            content = content.lower()
                        if pattern in content:
                            results.append(path)
                    except:
                        # Skip files that can't be read as text
                        pass
            
            except PermissionError:
                # Skip files we can't access
                continue
        
        return results


class FileHashTool(Tool[str]):
    """Calculate file hash for integrity verification"""
    
    def __init__(self):
        super().__init__(
            name="file_hash",
            category=ToolCategory.FILE_SYSTEM,
            description="Calculate cryptographic hash of files"
        )
    
    def validate_input(self, file_path: Union[str, Path], algorithm: str = "sha256") -> List[str]:
        """Validate hash parameters"""
        errors = []
        
        if not file_path:
            errors.append("File path is required")
            return errors
        
        path = Path(file_path)
        if not path.exists():
            errors.append(f"File does not exist: {path}")
        elif not path.is_file():
            errors.append(f"Path is not a file: {path}")
        
        valid_algorithms = ['md5', 'sha1', 'sha256', 'sha512']
        if algorithm not in valid_algorithms:
            errors.append(f"Invalid algorithm: {algorithm}. Must be one of {valid_algorithms}")
        
        return errors
    
    def dry_run(self, context: ToolContext, file_path: Union[str, Path], algorithm: str = "sha256") -> str:
        """Preview hash calculation"""
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            return f"Would calculate {algorithm} hash of {path} ({size} bytes)"
        return f"File does not exist: {path}"
    
    def _execute_impl(self, context: ToolContext, file_path: Union[str, Path], algorithm: str = "sha256") -> str:
        """Calculate file hash"""
        path = Path(file_path)
        
        # Get hash function
        hash_func = getattr(hashlib, algorithm)()
        
        # Read file in chunks to handle large files
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()