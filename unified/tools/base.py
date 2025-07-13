"""
Base Tool abstraction for safe execution
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ToolStatus(Enum):
    """Status of tool execution"""
    NOT_STARTED = "not_started"
    VALIDATING = "validating"
    DRY_RUN = "dry_run"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ToolCategory(Enum):
    """Categories of tools"""
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    PROCESS = "process"
    DATA_TRANSFORM = "data_transform"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    CODE_EXECUTION = "code_execution"
    FILE = "file"


@dataclass
class ToolContext:
    """Context for tool execution"""
    working_directory: Path
    user: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    timeout: Optional[float] = None
    dry_run: bool = False
    sandbox: bool = False
    environment: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult(Generic[T]):
    """Result of tool execution"""
    status: ToolStatus
    output: Optional[T] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    dry_run_preview: Optional[str] = None
    
    def __post_init__(self):
        if self.start_time and self.end_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
    
    @property
    def success(self) -> bool:
        return self.status == ToolStatus.COMPLETED
    
    @property
    def failed(self) -> bool:
        return self.status == ToolStatus.FAILED


class Tool(ABC, Generic[T]):
    """
    Abstract base class for all tools.
    Provides dry-run capability and safe execution.
    """
    
    def __init__(self, name: str, category: ToolCategory, description: str = ""):
        self.name = name
        self.category = category
        self.description = description
        self._validators: List[callable] = []
        self._status = ToolStatus.NOT_STARTED
        self._current_context: Optional[ToolContext] = None
    
    @abstractmethod
    def validate_input(self, *args, **kwargs) -> List[str]:
        """
        Validate input parameters.
        Returns list of validation errors, empty if valid.
        """
        pass
    
    @abstractmethod
    def dry_run(self, context: ToolContext, *args, **kwargs) -> str:
        """
        Perform a dry run showing what would happen.
        Returns a description of what would be executed.
        """
        pass
    
    @abstractmethod
    def _execute_impl(self, context: ToolContext, *args, **kwargs) -> T:
        """
        Actual implementation of tool execution.
        This is called by execute() after validation.
        """
        pass
    
    def execute(self, context: ToolContext, *args, **kwargs) -> ToolResult[T]:
        """
        Execute the tool with validation and error handling.
        """
        self._current_context = context
        result = ToolResult[T](
            status=ToolStatus.NOT_STARTED,
            start_time=datetime.now()
        )
        
        try:
            # Validation phase
            self._status = ToolStatus.VALIDATING
            errors = self.validate_input(*args, **kwargs)
            if errors:
                result.status = ToolStatus.FAILED
                result.error = f"Validation failed: {'; '.join(errors)}"
                result.end_time = datetime.now()
                return result
            
            # Run custom validators
            for validator in self._validators:
                try:
                    if not validator(context, *args, **kwargs):
                        result.status = ToolStatus.FAILED
                        result.error = f"Custom validation failed: {validator.__name__}"
                        result.end_time = datetime.now()
                        return result
                except Exception as e:
                    result.status = ToolStatus.FAILED
                    result.error = f"Validator error: {str(e)}"
                    result.end_time = datetime.now()
                    return result
            
            # Dry run if requested
            if context.dry_run:
                self._status = ToolStatus.DRY_RUN
                preview = self.dry_run(context, *args, **kwargs)
                result.status = ToolStatus.COMPLETED
                result.dry_run_preview = preview
                result.end_time = datetime.now()
                logger.info(f"Dry run completed for {self.name}: {preview}")
                return result
            
            # Execute
            self._status = ToolStatus.EXECUTING
            logger.info(f"Executing tool {self.name}")
            
            # Check if sandboxed execution is requested
            if context.sandbox and hasattr(self, '_execute_sandboxed'):
                output = self._execute_sandboxed(context, *args, **kwargs)
            elif context.timeout:
                # Execute with timeout
                output = asyncio.run(
                    self._execute_with_timeout(context, context.timeout, *args, **kwargs)
                )
            else:
                output = self._execute_impl(context, *args, **kwargs)
            
            result.status = ToolStatus.COMPLETED
            result.output = output
            result.end_time = datetime.now()
            logger.info(f"Tool {self.name} completed successfully")
            
        except asyncio.TimeoutError:
            result.status = ToolStatus.FAILED
            result.error = f"Execution timed out after {context.timeout} seconds"
            result.end_time = datetime.now()
            logger.error(f"Tool {self.name} timed out")
            
        except Exception as e:
            result.status = ToolStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.now()
            logger.error(f"Tool {self.name} failed: {e}")
        
        finally:
            self._status = result.status
            self._current_context = None
        
        return result
    
    async def _execute_with_timeout(self, context: ToolContext, timeout: float, *args, **kwargs) -> T:
        """Execute with timeout using asyncio"""
        loop = asyncio.get_event_loop()
        return await asyncio.wait_for(
            loop.run_in_executor(None, self._execute_impl, context, *args, **kwargs),
            timeout=timeout
        )
    
    def add_validator(self, validator: callable) -> None:
        """Add a custom validator function"""
        self._validators.append(validator)
    
    def get_status(self) -> ToolStatus:
        """Get current execution status"""
        return self._status
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get tool capabilities and metadata"""
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "supports_dry_run": True,
            "supports_timeout": True,
            "supports_sandbox": hasattr(self, '_execute_sandboxed')
        }


class AsyncTool(Tool[T], ABC):
    """
    Async version of Tool base class.
    """
    
    async def execute_async(self, context: ToolContext, *args, **kwargs) -> ToolResult[T]:
        """
        Execute the tool asynchronously.
        """
        self._current_context = context
        result = ToolResult[T](
            status=ToolStatus.NOT_STARTED,
            start_time=datetime.now()
        )
        
        try:
            # Validation phase
            self._status = ToolStatus.VALIDATING
            errors = self.validate_input(*args, **kwargs)
            if errors:
                result.status = ToolStatus.FAILED
                result.error = f"Validation failed: {'; '.join(errors)}"
                result.end_time = datetime.now()
                return result
            
            # Dry run if requested
            if context.dry_run:
                self._status = ToolStatus.DRY_RUN
                preview = self.dry_run(context, *args, **kwargs)
                result.status = ToolStatus.COMPLETED
                result.dry_run_preview = preview
                result.end_time = datetime.now()
                return result
            
            # Execute
            self._status = ToolStatus.EXECUTING
            
            if context.timeout:
                output = await asyncio.wait_for(
                    self._execute_async_impl(context, *args, **kwargs),
                    timeout=context.timeout
                )
            else:
                output = await self._execute_async_impl(context, *args, **kwargs)
            
            result.status = ToolStatus.COMPLETED
            result.output = output
            result.end_time = datetime.now()
            
        except asyncio.TimeoutError:
            result.status = ToolStatus.FAILED
            result.error = f"Execution timed out after {context.timeout} seconds"
            result.end_time = datetime.now()
            
        except Exception as e:
            result.status = ToolStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.now()
        
        finally:
            self._status = result.status
            self._current_context = None
        
        return result
    
    @abstractmethod
    async def _execute_async_impl(self, context: ToolContext, *args, **kwargs) -> T:
        """Async implementation of tool execution"""
        pass
    
    def _execute_impl(self, context: ToolContext, *args, **kwargs) -> T:
        """Sync wrapper for async implementation"""
        return asyncio.run(self._execute_async_impl(context, *args, **kwargs))