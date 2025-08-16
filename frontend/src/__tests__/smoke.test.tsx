import React from 'react';
import { render, screen } from '@testing-library/react';

function Hello() {
  return <div>hello world</div>;
}

describe('smoke test', () => {
  it('renders a simple component', () => {
    render(<Hello />);
    expect(screen.getByText(/hello world/i)).toBeInTheDocument();
  });
});

