import { API_BASE_URL } from '../config';

export const getImageUrl = (imageUrl: string | null | undefined): string => {
  if (!imageUrl) {
    return '/placeholder.png';  // Default placeholder image
  }

  // If it's already a full URL (e.g., https://...), return as is
  if (imageUrl.startsWith('http')) {
    return imageUrl;
  }

  // If it's a local path (e.g., /uploads/...), prefix with API base URL
  if (imageUrl.startsWith('/uploads/')) {
    return `${API_BASE_URL}${imageUrl}`;
  }

  // For any other case, assume it's a relative path and prefix with API base URL
  return `${API_BASE_URL}/uploads/${imageUrl}`;
};

// Enhanced version with cache-busting for newly uploaded images
export const getImageUrlWithCacheBust = (imageUrl: string | null | undefined, itemCreatedAt?: string): string => {
  const baseUrl = getImageUrl(imageUrl);
  
  if (baseUrl === '/placeholder.png') {
    return baseUrl;
  }
  
  // Add cache-busting parameter for images from items created in the last 5 minutes
  if (itemCreatedAt) {
    const createdDate = new Date(itemCreatedAt);
    const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
    
    if (createdDate > fiveMinutesAgo) {
      const separator = baseUrl.includes('?') ? '&' : '?';
      return `${baseUrl}${separator}t=${Date.now()}`;
    }
  }
  
  return baseUrl;
};