"""Tests for FileEditObservation class."""

from openhands.events.event import FileEditSource
from openhands.events.observation.files import FileEditObservation

def test_file_edit_observation_basic():
    """Test basic properties of FileEditObservation."""
    obs = FileEditObservation(
        path='/test/file.txt',
        prev_exist=True,
        old_content='Hello\nWorld\n',
        new_content='Hello\nNew World\n',
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content='Hello\nWorld\n',  # Initial content is old_content
    )

    assert obs.path == '/test/file.txt'
    assert obs.prev_exist is True
    assert obs.old_content == 'Hello\nWorld\n'
    assert obs.new_content == 'Hello\nNew World\n'
    assert obs.impl_source == FileEditSource.LLM_BASED_EDIT
    assert obs.message == 'I edited the file /test/file.txt.'

def test_file_edit_observation_diff_cache():
    """Test that diff visualization is cached."""
    obs = FileEditObservation(
        path='/test/file.txt',
        prev_exist=True,
        old_content='Hello\nWorld\n',
        new_content='Hello\nNew World\n',
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content='Hello\nWorld\n',  # Initial content is old_content
    )

    # First call should compute diff
    diff1 = obs.visualize_diff()
    assert obs._diff_cache is not None

    # Second call should use cache
    diff2 = obs.visualize_diff()
    assert diff1 == diff2

def test_file_edit_observation_no_changes():
    """Test behavior when content hasn't changed."""
    content = 'Hello\nWorld\n'
    obs = FileEditObservation(
        path='/test/file.txt',
        prev_exist=True,
        old_content=content,
        new_content=content,
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content=content,  # Initial content is old_content
    )

    diff = obs.visualize_diff()
    assert '(no changes detected' in diff

def test_file_edit_observation_get_edit_groups():
    """Test the get_edit_groups method."""
    obs = FileEditObservation(
        path='/test/file.txt',
        prev_exist=True,
        old_content='Line 1\nLine 2\nLine 3\nLine 4\n',
        new_content='Line 1\nNew Line 2\nLine 3\nNew Line 4\n',
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content='Line 1\nLine 2\nLine 3\nLine 4\n',  # Initial content is old_content
    )

    groups = obs.get_edit_groups(n_context_lines=1)
    assert len(groups) > 0

    # Check structure of edit groups
    for group in groups:
        assert 'before_edits' in group
        assert 'after_edits' in group
        assert isinstance(group['before_edits'], list)
        assert isinstance(group['after_edits'], list)

    # Verify line numbers and content
    first_group = groups[0]
    assert any('Line 2' in line for line in first_group['before_edits'])
    assert any('New Line 2' in line for line in first_group['after_edits'])

def test_file_edit_observation_new_file():
    """Test behavior when editing a new file."""
    obs = FileEditObservation(
        path='/test/new_file.txt',
        prev_exist=False,
        old_content='',
        new_content='Hello\nWorld\n',
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content='',  # Initial content is old_content (empty for new file)
    )

    assert obs.prev_exist is False
    assert obs.old_content == ''
    assert (
        str(obs)
        == '[New file /test/new_file.txt is created with the provided content.]\n'
    )

    # Test that trying to visualize diff for a new file works
    diff = obs.visualize_diff()
    assert diff is not None

def test_file_edit_observation_context_lines():
    """Test diff visualization with different context line settings."""
    obs = FileEditObservation(
        path='/test/file.txt',
        prev_exist=True,
        old_content='Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n',
        new_content='Line 1\nNew Line 2\nLine 3\nNew Line 4\nLine 5\n',
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content='Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n',  # Initial content is old_content
    )

    # Test with 0 context lines
    groups_0 = obs.get_edit_groups(n_context_lines=0)
    # Test with 2 context lines
    groups_2 = obs.get_edit_groups(n_context_lines=2)

    # More context should mean more lines in the groups
    total_lines_0 = sum(
        len(g['before_edits']) + len(g['after_edits']) for g in groups_0
    )
    total_lines_2 = sum(
        len(g['before_edits']) + len(g['after_edits']) for g in groups_2
    )
    assert total_lines_2 > total_lines_0

# New tests for the get_edit_summary method
def test_edit_summary_new_file():
    """Test edit summary when creating a new file (prev_exist=False)."""
    obs = FileEditObservation(
        path='/test/new_file.py',
        prev_exist=False,
        old_content='',
        new_content='print("Hello, world!")\n',
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content='',  # Initial content for new file
    )

    summary = obs.get_edit_summary()
    assert summary['type'] == 'new_file'
    # No language field in the summary for new files

def test_edit_summary_modification():
    """Test edit summary when modifying an existing file."""
    old_content = 'print("Hello")\n'
    new_content = 'print("Hello, world!")\n'

    obs = FileEditObservation(
        path='/test/file.py',
        prev_exist=True,
        old_content=old_content,
        new_content=new_content,
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content=old_content,  # Initial content is old_content
    )

    summary = obs.get_edit_summary()
    assert summary['type'] == 'modification'
    assert summary['total_changes'] > 0
    assert len(summary['edit_groups']) > 0

def test_edit_summary_no_changes():
    """Test edit summary when there are no changes."""
    content = 'print("Hello, world!")\n'

    obs = FileEditObservation(
        path='/test/file.py',
        prev_exist=True,
        old_content=content,
        new_content=content,
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content=content,  # Initial content is old_content
    )

    summary = obs.get_edit_summary()
    assert summary['type'] == 'modification'  # Actual behavior

def test_edit_summary_structure():
    """Test the structure of edit summary."""
    old_content = 'line1\nline2\nline3\n'
    new_content = 'line1\nNEW_line2\nline3\n'

    obs = FileEditObservation(
        path='/test/file.txt',
        prev_exist=True,
        old_content=old_content,
        new_content=new_content,
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content=old_content,  # Initial content is old_content
    )

    summary = obs.get_edit_summary()
    assert 'type' in summary
    assert 'total_changes' in summary
    assert 'has_syntax_highlighting' in summary
    assert 'language' in summary
    assert 'edit_groups' in summary

    # Check edit groups structure
    for group in summary['edit_groups']:
        assert 'before_edits' in group
        assert 'after_edits' in group
        assert isinstance(group['before_edits'], list)
        assert isinstance(group['after_edits'], list)

def test_edit_summary_language_detection():
    """Test language detection based on file extension."""
    # Test with various file extensions
    extensions = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.html': 'html',
        '.md': 'markdown',
        '.txt': 'plaintext',  # Default for unknown extensions
    }

    old_content = 'some content\n'
    new_content = 'modified content\n'

    for ext, expected_lang in extensions.items():
        obs = FileEditObservation(
            path=f'/test/file{ext}',
            prev_exist=True,
            old_content=old_content,
            new_content=new_content,
            impl_source=FileEditSource.LLM_BASED_EDIT,
            content=old_content,  # Initial content is old_content
        )

        summary = obs.get_edit_summary()
        assert summary['language'] == expected_lang


