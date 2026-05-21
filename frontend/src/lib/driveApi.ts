import { api, clearAccessToken, setAccessToken, unwrap } from './api'
import type { BreadcrumbItem, DriveNode, FolderTreeItem } from '../types/node'

export async function fetchRootId(): Promise<string> {
  const res = await api.get('/nodes/root')
  return unwrap<{ id: string }>(res.data).id
}

export async function listChildren(parentId: string): Promise<DriveNode[]> {
  const res = await api.get('/nodes', { params: { parent_id: parentId } })
  return unwrap<DriveNode[]>(res.data)
}

export async function fetchBreadcrumb(nodeId: string): Promise<BreadcrumbItem[]> {
  const res = await api.get(`/nodes/${nodeId}/breadcrumb`)
  return unwrap<BreadcrumbItem[]>(res.data)
}

export async function fetchFolderTree(): Promise<FolderTreeItem[]> {
  const res = await api.get('/nodes/folders/tree')
  return unwrap<FolderTreeItem[]>(res.data)
}

export async function createFolder(
  parentId: string,
  name: string,
): Promise<DriveNode> {
  const res = await api.post('/nodes/folder', { parent_id: parentId, name })
  return unwrap<DriveNode>(res.data)
}

export async function uploadFile(parentId: string, file: File): Promise<DriveNode> {
  const fd = new FormData()
  fd.append('parent_id', parentId)
  fd.append('file', file)
  const res = await api.post('/nodes/upload', fd)
  return unwrap<DriveNode>(res.data)
}

/** 相对路径，适合当前站点内 <a href> / window.open（会带上 Cookie） */
export function downloadUrl(nodeId: string): string {
  return `/api/nodes/${nodeId}/download`
}

export function thumbnailUrl(nodeId: string, size = 200): string {
  return `/api/nodes/${nodeId}/thumbnail?size=${size}`
}

/** 浏览器可复制的完整 URL（公开下载，无需登录；请当作「谁拿到谁就能下」的私密链接） */
export function absoluteDownloadUrl(nodeId: string): string {
  if (typeof window === 'undefined') {
    return downloadUrl(nodeId)
  }
  const basePath = (import.meta.env.BASE_URL ?? '/').replace(/\/+$/, '')
  const apiPath = downloadUrl(nodeId)
  const fullPath = `${basePath}${apiPath.startsWith('/') ? apiPath : `/${apiPath}`}`
  return new URL(fullPath, window.location.origin).toString()
}

export async function renameNode(nodeId: string, name: string): Promise<DriveNode> {
  const res = await api.patch(`/nodes/${nodeId}/rename`, { name })
  return unwrap<DriveNode>(res.data)
}

export async function moveNode(nodeId: string, parentId: string): Promise<DriveNode> {
  const res = await api.post(`/nodes/${nodeId}/move`, { parent_id: parentId })
  return unwrap<DriveNode>(res.data)
}

export async function deleteNode(nodeId: string): Promise<void> {
  await api.delete(`/nodes/${nodeId}`)
}

export async function reparseNodeMeta(nodeId: string): Promise<DriveNode> {
  const res = await api.post(`/nodes/${nodeId}/reparse-meta`)
  return unwrap<DriveNode>(res.data)
}

export async function register(username: string, password: string): Promise<void> {
  await api.post('/auth/register', { username, password })
}

export async function login(username: string, password: string): Promise<void> {
  const res = await api.post('/auth/login', { username, password })
  const payload = unwrap<{ access_token: string; token_type: string; username: string }>(res.data)
  setAccessToken(payload.access_token)
}

export async function logout(): Promise<void> {
  try {
    await api.post('/auth/logout')
  } finally {
    clearAccessToken()
  }
}

export async function me(): Promise<{ username: string }> {
  const res = await api.get('/auth/me')
  return unwrap<{ username: string }>(res.data)
}
