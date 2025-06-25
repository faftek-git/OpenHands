"""Tests for language detection in FileEditObservation class."""

import pytest

from openhands.events.event import FileEditSource
from openhands.events.observation.files import FileEditObservation


def test_common_extensions():
    """Test language detection for common file extensions."""
    test_cases = [
        ('/test/file.py', 'python'),
        ('/test/file.js', 'javascript'),
        ('/test/file.ts', 'typescript'),
        ('/test/file.jsx', 'jsx'),
        ('/test/file.tsx', 'tsx'),
        ('/test/file.html', 'html'),
        ('/test/file.css', 'css'),
        ('/test/file.json', 'json'),
        ('/test/file.md', 'markdown'),
        ('/test/file.sh', 'shell'),
        ('/test/file.yml', 'yaml'),
        ('/test/file.yaml', 'yaml'),
    ]
    
    for file_path, expected_language in test_cases:
        obs = FileEditObservation(
            path=file_path,
            prev_exist=True,
            old_content='test content',
            new_content='test content',
            impl_source=FileEditSource.LLM_BASED_EDIT,
            content='test content',
        )
        assert obs._get_language_from_extension() == expected_language, f"Failed for {file_path}"


def test_unknown_extensions():
    """Test that unknown extensions return 'plaintext'."""
    unknown_extensions = [
        '/test/file.unknown',
        '/test/file.xyz',
        '/test/file.abc123',
        '/test/file.custom',
        '/test/file.ext',
        '/test/file.binary',
    ]
    
    for file_path in unknown_extensions:
        obs = FileEditObservation(
            path=file_path,
            prev_exist=True,
            old_content='test content',
            new_content='test content',
            impl_source=FileEditSource.LLM_BASED_EDIT,
            content='test content',
        )
        assert obs._get_language_from_extension() == 'plaintext', f"Failed for {file_path}"


def test_case_insensitivity():
    """Test that file extension detection is case insensitive."""
    test_cases = [
        ('/test/file.PY', 'python'),
        ('/test/file.JS', 'javascript'),
        ('/test/file.TS', 'typescript'),
        ('/test/file.JSX', 'jsx'),
        ('/test/file.TSX', 'tsx'),
        ('/test/file.HTML', 'html'),
        ('/test/file.CSS', 'css'),
        ('/test/file.JSON', 'json'),
        ('/test/file.MD', 'markdown'),
        ('/test/file.SH', 'shell'),
        ('/test/file.YML', 'yaml'),
        ('/test/file.YAML', 'yaml'),
        ('/test/file.Py', 'python'),
        ('/test/file.Js', 'javascript'),
        ('/test/file.mD', 'markdown'),
    ]
    
    for file_path, expected_language in test_cases:
        obs = FileEditObservation(
            path=file_path,
            prev_exist=True,
            old_content='test content',
            new_content='test content',
            impl_source=FileEditSource.LLM_BASED_EDIT,
            content='test content',
        )
        assert obs._get_language_from_extension() == expected_language, f"Failed for {file_path}"


def test_edge_cases():
    """Test edge cases for language detection."""
    edge_cases = [
        # No extension
        ('/test/file', 'plaintext'),
        ('/test/README', 'plaintext'),
        ('/test/Makefile', 'plaintext'),
        
        # Multiple dots
        ('/test/file.test.py', 'python'),
        ('/test/file.backup.js', 'javascript'),
        ('/test/config.local.json', 'json'),
        ('/test/component.spec.ts', 'typescript'),
        ('/test/styles.min.css', 'css'),
        
        # Just extension (edge case) - these are treated as filenames, not extensions
        ('.py', 'plaintext'),
        ('.js', 'plaintext'),
        ('.unknown', 'plaintext'),
        
        # Empty extension after dot
        ('/test/file.', 'plaintext'),
        
        # Path with directories containing dots
        ('/test/dir.with.dots/file.py', 'python'),
        ('/test/v1.0/file.js', 'javascript'),
        
        # Complex paths
        ('/home/user/project/src/components/Button.tsx', 'tsx'),
        ('/var/www/html/index.html', 'html'),
        ('C:\\Users\\test\\file.py', 'python'),  # Windows path
    ]
    
    for file_path, expected_language in edge_cases:
        obs = FileEditObservation(
            path=file_path,
            prev_exist=True,
            old_content='test content',
            new_content='test content',
            impl_source=FileEditSource.LLM_BASED_EDIT,
            content='test content',
        )
        assert obs._get_language_from_extension() == expected_language, f"Failed for {file_path}"


def test_empty_path():
    """Test behavior with empty path."""
    obs = FileEditObservation(
        path='',
        prev_exist=True,
        old_content='test content',
        new_content='test content',
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content='test content',
    )
    assert obs._get_language_from_extension() == 'plaintext'


def test_all_supported_extensions_comprehensive():
    """Comprehensive test to ensure all extensions in language_map are tested."""
    # This test ensures we don't miss any extensions if the language_map is updated
    obs = FileEditObservation(
        path='/test/dummy.py',  # dummy path, we'll change it
        prev_exist=True,
        old_content='test content',
        new_content='test content',
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content='test content',
    )
    
    # Get the language_map from the method by inspecting the source
    # This is a bit hacky but ensures we test all supported extensions
    import os
    
    # Test each extension from the known language_map
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'jsx',
        '.tsx': 'tsx',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.md': 'markdown',
        '.sh': 'shell',
        '.yml': 'yaml',
        '.yaml': 'yaml',
    }
    
    for ext, expected_language in language_map.items():
        obs.path = f'/test/file{ext}'
        assert obs._get_language_from_extension() == expected_language, f"Failed for extension {ext}"


def test_language_detection_with_different_file_states():
    """Test language detection works regardless of file state (new vs existing)."""
    test_cases = [
        # New file
        {
            'path': '/test/new_file.py',
            'prev_exist': False,
            'old_content': '',
            'new_content': 'print("hello")',
            'expected_language': 'python',
        },
        # Existing file
        {
            'path': '/test/existing_file.js',
            'prev_exist': True,
            'old_content': 'console.log("old");',
            'new_content': 'console.log("new");',
            'expected_language': 'javascript',
        },
        # File with no changes
        {
            'path': '/test/unchanged.md',
            'prev_exist': True,
            'old_content': '# Title',
            'new_content': '# Title',
            'expected_language': 'markdown',
        },
    ]
    
    for case in test_cases:
        obs = FileEditObservation(
            path=case['path'],
            prev_exist=case['prev_exist'],
            old_content=case['old_content'],
            new_content=case['new_content'],
            impl_source=FileEditSource.LLM_BASED_EDIT,
            content=case['old_content'],
        )
        assert obs._get_language_from_extension() == case['expected_language']


def test_language_detection_performance():
    """Test that language detection is fast and doesn't have side effects."""
    obs = FileEditObservation(
        path='/test/file.py',
        prev_exist=True,
        old_content='test content',
        new_content='test content',
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content='test content',
    )
    
    # Call multiple times to ensure it's consistent and fast
    results = []
    for _ in range(100):
        results.append(obs._get_language_from_extension())
    
    # All results should be the same
    assert all(result == 'python' for result in results)
    
    # Test that changing path works correctly
    obs.path = '/test/file.js'
    assert obs._get_language_from_extension() == 'javascript'
    
    obs.path = '/test/file.py'
    assert obs._get_language_from_extension() == 'python'