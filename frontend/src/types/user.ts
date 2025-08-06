export interface User {
    id: string;
    name: string;
    email: string;
    role: string;
    created_at: string;
    updated_at: string;
    item_count: number;
    lost_count: number;
    found_count: number;
    returned_count: number;
  }
  
  export interface UserStats {
    totalUsers: number;
    activeUsers: number;
    adminUsers: number;
    regularUsers: number;
    todayUsers: number;
    weekUsers: number;
  } 