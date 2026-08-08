export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role_id: number
  is_active: boolean
}

export interface Product {
  id: number
  barcode: string
  product_code: string | null
  description: string
  unit_of_measure: string
  system_quantity: number
  unit_cost: number
  created_at: string
  updated_at: string
}

export interface Count {
  id: number
  product_id: number
  section_id: number
  quantity: number
  user_id: number
  session_id: number
  counted_at: string
  synced_at: string | null
  is_synced: boolean
}

export interface Session {
  id: number
  name: string
  description: string | null
  location_id: number
  start_time: string | null
  end_time: string | null
  status: string
  created_by: number
  created_at: string
  updated_at: string
}
