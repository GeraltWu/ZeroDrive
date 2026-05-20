export interface DriveNode {
  id: string
  parent_id: string | null
  name: string
  is_folder: boolean
  size: number
  mime_type: string | null
  meta_json: Record<string, unknown> | null
  updated_at: string
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
