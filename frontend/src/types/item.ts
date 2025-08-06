export enum ItemCategory {
    ELECTRONICS = 'electronics',
    ACCESSORIES = 'accessories',
    CLOTHING = 'clothing',
    BOOKS = 'books',
    DOCUMENTS = 'documents',
    OTHER = 'other'
  }
  
  export enum ItemStatus {
    LOST = 'lost',
    FOUND = 'found',
    CLAIMED = 'claimed',
    RETURNED = 'returned'
  }
  
  export enum ItemCustodyStatus {
    KEPT_BY_FINDER = 'kept_by_finder',
    HANDED_TO_ONE_STOP = 'handed_to_one_stop',
    LEFT_WHERE_FOUND = 'left_where_found'
  }
  
  export interface User {
    id: string;
    name: string;
    email: string;
    created_at: string;
  }
  
  export interface Item {
    id: string;
    title: string;
    description: string;
    category: ItemCategory;
    status: ItemStatus;
    location_found?: string;  // Made optional for backward compatibility
    location?: string;        // Added for new items
    date_found: string;
    image_url: string | null;
    finder_id?: string;
    user_id: string;
    user_name?: string;
    created_at: string;
    updated_at?: string;
    user?: User;
    custody_status?: ItemCustodyStatus;  // New field for where the item is
  } 