import React from 'react';
import { render } from '@testing-library/react';
import { FileEditViewer, FileEditViewerProps } from './file-edit-viewer';

describe('FileEditViewer', () => {
  const defaultProps: FileEditViewerProps = {
    filePath: '/path/to/file.txt',
    oldContent: 'Old content',
    newContent: 'New content',
  };

  it('should render without crashing', () => {
    render(<FileEditViewer {...defaultProps} />);
  });
});


