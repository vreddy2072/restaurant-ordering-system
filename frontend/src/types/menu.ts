export interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: number;
  category_id: number;
  category: string;
  is_active: boolean;
  is_available: boolean;
  is_vegetarian: boolean;
  is_vegan: boolean;
  is_gluten_free: boolean;
  spice_level: number;
  preparation_time: number;
  average_rating: number;
  rating_count: number;
  allergens: Allergen[];
  customization_options: {
    [key: string]: string[];
  };
  image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate {
  name: string;
  description: string | null;
  is_active: boolean;
}

export interface CategoryUpdate extends CategoryCreate {
  id?: never;
}

export interface Allergen {
  id: number;
  name: string;
  description?: string;
}

export interface MenuItemCreate extends Omit<MenuItem, 'id' | 'created_at' | 'updated_at' | 'category' | 'average_rating' | 'rating_count'> {
  category_id: number;
  allergen_ids: number[];
}

export interface MenuItemUpdate extends Partial<MenuItemCreate> {
  id?: never;
}