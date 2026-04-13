export interface BrandMini {
  id: number;
  name: string;
}

export interface CategoryMini {
  id: number;
  name: string;
}

export interface ProductListItem {
  id: number;
  name: string;
  slug: string;
  price: string | number;
  discount_price: string | number | null;
  rating: string | number;
  review_count: number;
  stock_quantity: number;
  brand: BrandMini;
  category: CategoryMini;
  primary_image: string | null;
}

export interface ProductImage {
  id: number;
  image_url: string;
  is_primary: boolean;
}

export interface ProductAttribute {
  attribute_name: string;
  attribute_value: string;
}

export interface ProductDetail extends Omit<ProductListItem, "primary_image"> {
  short_description: string;
  description: string;
  is_active: boolean;
  images: ProductImage[];
  tags: string[];
  attributes: ProductAttribute[];
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  parent: number | null;
}

export interface Brand {
  id: number;
  name: string;
  slug: string;
}
