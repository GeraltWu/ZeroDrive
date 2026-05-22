export interface DriveNode {
  id: string
  parent_id: string | null
  name: string
  is_folder: boolean
  size: number
  mime_type: string | null
  meta_json: Record<string, unknown> | null
  owner_id: string | null
  owner_username: string | null
  updated_at: string
}

export interface Collaborator {
  id: string
  folder_id: string
  user_id: string
  username: string
  role: string
  created_at: string
}

export interface SharedFolder {
  folder_id: string
  folder_name: string
  role: string
}

export interface BreadcrumbItem {
  id: string
  name: string
}

export interface FolderTreeItem {
  id: string
  parent_id: string | null
  name: string
}

export interface FolderTreeNode extends FolderTreeItem {
  children: FolderTreeNode[]
}
