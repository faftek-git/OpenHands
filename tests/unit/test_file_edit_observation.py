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


def test_edit_summary_new_file():
    """Test get_edit_summary() method with a new file."""
    obs = FileEditObservation(
        path='/test/new_file.txt',
        prev_exist=False,
        old_content='',
        new_content='Hello\nWorld\n',
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content='',  # Initial content is empty for new file
    )

    summary = obs.get_edit_summary()
    assert 'file_path' in summary
    assert summary['file_path'] == '/test/new_file.txt'
    assert summary['is_new_file'] is True
    assert 'num_lines' in summary
    assert summary['num_lines'] == 3  # Two lines: "Hello" and "World"
    assert 'changes' not in summary


def test_edit_summary_no_changes():
    """Test get_edit_summary() method with no changes."""
    content = 'Hello\nWorld\n'
    obs = FileEditObservation(
        path='/test/file.txt',
        prev_exist=True,
        old_content=content,
        new_content=content,
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content=content,  # Initial content is same as both
    )

    summary = obs.get_edit_summary()
    assert 'file_path' in summary
    assert not summary['is_new_file']
    assert 'num_lines_added' in summary
    assert 'num_lines_removed' in summary
    assert summary['num_lines_added'] == 0
    assert summary['num_lines_removed'] == 0


def test_edit_summary_modification():
    """Test get_edit_summary() method with file modifications."""
    obs = FileEditObservation(
        path='/test/file.txt',
        prev_exist=True,
        old_content='Line 1\nLine 2\nLine 3\n',
        new_content='Line 1\nNew Line 2\nLine 3\nLine 4\n',
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content='Line 1\nLine 2\nLine 3\n',  # Initial content is old_content
    )

    summary = obs.get_edit_summary()
    assert 'file_path' in summary
    assert not summary['is_new_file']
    assert 'changes' in summary
    assert len(summary['changes']) > 0

    # Check that the changes are properly reported
    change = summary['changes'][0]
    assert 'description' in change
    assert 'lines_added' in change
    assert 'lines_removed' in change

    # One line removed, one line added
    assert summary['num_lines_added'] == 2  # Added Line 4 and modified Line 2
    assert summary['num_lines_removed'] == 1  # Removed original Line 2


def test_edit_summary_structure():
    """Test the structure of the dictionary returned by get_edit_summary()."""
    obs = FileEditObservation(
        path='/test/file.txt',
        prev_exist=True,
        old_content='Line 1\nLine 2\nLine 3\n',
        new_content='Line 1\nNew Line 2\nLine 3\nLine 4\n',
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content='Line 1\nLine 2\nLine 3\n',  # Initial content is old_content
    )

    summary = obs.get_edit_summary()

    # Check required fields
    assert 'file_path' in summary
    assert isinstance(summary['is_new_file'], bool)

    # For existing files, these should be populated
    assert 'changes' in summary
    assert isinstance(summary['changes'], list)
    for change in summary['changes']:
        assert 'description' in change
        assert isinstance(change['lines_added'], int)
        assert isinstance(change['lines_removed'], int)

    # Sample data should be included when available
    if len(summary['changes']) > 0:
        first_change = summary['changes'][0]
        assert 'before_samples' in first_change
        assert 'after_samples' in first_change
        assert isinstance(first_change['before_samples'], list)
        assert isinstance(first_change['after_samples'], list)


def test_edit_summary_edge_cases():
    """Test get_edit_summary() with edge cases like None content."""
    obs = FileEditObservation(
        path='/test/file.txt',
        prev_exist=True,
        old_content=None,
        new_content='New content\n',
        impl_source=FileEditSource.LLM_BASED_EDIT,
        content='',  # Need to provide a non-None content
    )

    summary = obs.get_edit_summary()
    assert 'file_path' in summary
    assert not summary['is_new_file']
    assert 'changes' in summary
    assert len(summary['changes']) == 0
