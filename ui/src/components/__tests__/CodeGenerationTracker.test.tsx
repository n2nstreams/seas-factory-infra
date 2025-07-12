import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { jest } from '@jest/globals';
import CodeGenerationTracker from '../CodeGenerationTracker';

// Mock the useWebSocket hook
jest.mock('../hooks/useWebSocket', () => ({
  useWebSocket: jest.fn(() => ({
    isConnected: true,
    connectionStatus: 'connected',
    lastMessage: null,
    reconnectAttempts: 0,
    connect: jest.fn(),
    disconnect: jest.fn(),
    sendMessage: jest.fn()
  }))
}));

// Mock fetch
global.fetch = jest.fn();

describe('CodeGenerationTracker', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders code generation tracker', () => {
    render(<CodeGenerationTracker />);
    
    expect(screen.getByText('Code Generation Progress')).toBeInTheDocument();
    expect(screen.getByText('Live')).toBeInTheDocument();
    expect(screen.getByText('Pause')).toBeInTheDocument();
    expect(screen.getByText('Refresh')).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    render(<CodeGenerationTracker />);
    
    expect(screen.getByText('Loading code generation tasks...')).toBeInTheDocument();
  });

  it('shows empty state when no tasks', async () => {
    const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ tasks: [] })
    } as Response);

    render(<CodeGenerationTracker />);
    
    await waitFor(() => {
      expect(screen.getByText('No active code generation tasks')).toBeInTheDocument();
    });
  });

  it('displays tasks when available', async () => {
    const mockTasks = [
      {
        id: '1',
        project_id: 'test-project',
        module_name: 'TestModule',
        module_type: 'service',
        language: 'python',
        framework: 'fastapi',
        status: 'generating',
        progress: 45,
        current_stage: 'Generating code with GPT-4o...',
        created_at: '2024-01-01T10:00:00Z',
        updated_at: '2024-01-01T10:05:00Z',
        total_files: 3,
        total_lines: 150
      }
    ];

    const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ tasks: mockTasks })
    } as Response);

    render(<CodeGenerationTracker />);
    
    await waitFor(() => {
      expect(screen.getByText('TestModule')).toBeInTheDocument();
      expect(screen.getByText('python')).toBeInTheDocument();
      expect(screen.getByText('fastapi')).toBeInTheDocument();
      expect(screen.getByText('45%')).toBeInTheDocument();
    });
  });

  it('shows error state when fetch fails', async () => {
    const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    render(<CodeGenerationTracker />);
    
    await waitFor(() => {
      expect(screen.getByText('Error loading tasks')).toBeInTheDocument();
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('handles WebSocket connection status', () => {
    const mockUseWebSocket = require('../hooks/useWebSocket').useWebSocket;
    mockUseWebSocket.mockReturnValue({
      isConnected: false,
      connectionStatus: 'disconnected',
      lastMessage: null,
      reconnectAttempts: 0,
      connect: jest.fn(),
      disconnect: jest.fn(),
      sendMessage: jest.fn()
    });

    render(<CodeGenerationTracker />);
    
    expect(screen.getByText('Disconnected')).toBeInTheDocument();
  });
}); 