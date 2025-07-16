/// <reference types="@testing-library/jest-dom" />
import React from 'react';
import { render, screen, waitFor, within, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import axios from 'axios';
import ItemList from '../ItemList';
import { useAuth } from '../../context/AuthContext';
import '@testing-library/jest-dom';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock useAuth hook
jest.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    token: 'test-token',
    user: { id: '1', email: 'test@example.com' },
  }),
}));

const mockItems = [
  {
    id: '1',
    title: 'Lost Phone',
    description: 'iPhone 12 Pro Max',
    category: 'electronics',
    status: 'lost',
    location_found: 'Library',
    date_found: '2024-03-20',
    image_url: null,
    finder_id: '1',
    created_at: '2024-03-20T10:00:00Z',
  },
  {
    id: '2',
    title: 'Found Keys',
    description: 'Car keys with red keychain',
    category: 'accessories',
    status: 'found',
    location_found: 'Parking Lot',
    date_found: '2024-03-19',
    image_url: null,
    finder_id: '2',
    created_at: '2024-03-19T15:00:00Z',
  },
];

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('ItemList Component', () => {
  beforeEach(() => {
    mockedAxios.get.mockReset();
  });

  it('renders loading state initially', async () => {
    mockedAxios.get.mockImplementationOnce(() => new Promise(() => {}));
    await act(async () => {
      renderWithRouter(<ItemList />);
    });
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders items after successful fetch', async () => {
    mockedAxios.get.mockResolvedValueOnce({ data: { items: mockItems, total: 2 } });
    await act(async () => {
      renderWithRouter(<ItemList />);
    });

    await waitFor(() => {
      expect(screen.getByText('Lost Phone')).toBeInTheDocument();
      expect(screen.getByText('Found Keys')).toBeInTheDocument();
    });
  });

  it('renders error message on fetch failure', async () => {
    mockedAxios.get.mockRejectedValueOnce(new Error('Failed to fetch'));
    await act(async () => {
      renderWithRouter(<ItemList />);
    });

    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch items/i)).toBeInTheDocument();
    });
  });

  it('filters items by search term', async () => {
    mockedAxios.get.mockResolvedValueOnce({ data: { items: mockItems, total: 2 } });
    await act(async () => {
      renderWithRouter(<ItemList />);
    });

    const searchInput = screen.getByLabelText('Search items');
    await act(async () => {
      await userEvent.type(searchInput, 'phone');
    });

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/items'),
        expect.objectContaining({
          params: expect.objectContaining({ search: 'phone' }),
        })
      );
    });
  });

  it('renders category filter', async () => {
    mockedAxios.get.mockResolvedValueOnce({ data: { items: mockItems, total: 2 } });
    await act(async () => {
      renderWithRouter(<ItemList />);
    });

    expect(screen.getByTestId('category-select')).toBeInTheDocument();
    expect(screen.getByLabelText('Category')).toBeInTheDocument();
  });

  it('handles pagination', async () => {
    mockedAxios.get.mockResolvedValueOnce({
      data: { items: mockItems, total: 20 },
    });
    await act(async () => {
      renderWithRouter(<ItemList />);
    });

    const page2Button = screen.getByRole('button', { name: /page 2/i });
    await act(async () => {
      await userEvent.click(page2Button);
    });

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/items'),
        expect.objectContaining({
          params: expect.objectContaining({ page: 2 }),
        })
      );
    });
  });
}); 