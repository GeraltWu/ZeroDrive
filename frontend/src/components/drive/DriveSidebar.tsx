import { useEffect, useState } from 'react'
import { Divider, NavLink, Paper, Text } from '@mantine/core'
import { IconFolder } from '@tabler/icons-react'
import { FolderTree } from './FolderTree'
import * as driveApi from '../../lib/driveApi'
import type { DriveNode, FolderTreeItem, SharedFolder } from '../../types/node'

export function DriveSidebar({
  flatFolders,
  rootId,
  folderId,
  onTreeSelect,
  draggingNodeId,
  refreshKey,
  favoriteNodes,
  onFavoriteContextMenu,
  onSharedFolderContextMenu,
}: {
  flatFolders: FolderTreeItem[]
  rootId: string | null
  folderId: string | null
  onTreeSelect: (id: string) => void
  draggingNodeId: string | null
  refreshKey: number
  favoriteNodes: DriveNode[]
  onFavoriteContextMenu: (node: DriveNode, x: number, y: number) => void
  onSharedFolderContextMenu: (sf: SharedFolder, x: number, y: number) => void
}) {
  const [sharedFolders, setSharedFolders] = useState<SharedFolder[]>([])

  useEffect(() => {
    void driveApi.listSharedWithMe().then(setSharedFolders)
  }, [refreshKey])

  if (!rootId) return null

  const folderFavs = favoriteNodes.filter((f) => f.is_folder)

  return (
    <Paper withBorder p={6} w={300} miw={300} maw={300} style={{ flexShrink: 0 }}>
      <Text size="xs" c="dimmed" mb="xs" fw={600}>
        文件夹
      </Text>
      <FolderTree
        flat={flatFolders}
        rootId={rootId}
        selectedId={folderId ?? ''}
        onSelect={(id) => void onTreeSelect(id)}
        draggingNodeId={draggingNodeId}
      />

      {folderFavs.length > 0 && (
        <>
          <Divider my="sm" />
          <Text size="xs" c="dimmed" mb="xs" fw={600}>
            收藏夹
          </Text>
          {folderFavs.map((f) => (
            <NavLink
              key={f.id}
              label={f.name}
              leftSection={<IconFolder size={16} />}
              active={folderId === f.id}
              onClick={() => onTreeSelect(f.id)}
              onContextMenu={(e) => {
                e.preventDefault()
                onFavoriteContextMenu(f, e.clientX, e.clientY)
              }}
              style={{ borderRadius: 4 }}
            />
          ))}
        </>
      )}

      {sharedFolders.length > 0 && (
        <>
          <Divider my="sm" />
          <Text size="xs" c="dimmed" mb="xs" fw={600}>
            与我共享
          </Text>
          {sharedFolders.map((sf) => (
            <NavLink
              key={sf.folder_id}
              label={sf.folder_name}
              leftSection={<IconFolder size={16} />}
              active={folderId === sf.folder_id}
              onClick={() => onTreeSelect(sf.folder_id)}
              onContextMenu={(e) => {
                e.preventDefault()
                onSharedFolderContextMenu(sf, e.clientX, e.clientY)
              }}
              description={sf.role === 'viewer' ? '只读' : sf.role === 'editor' ? '可编辑' : '管理员'}
              style={{ borderRadius: 4 }}
            />
          ))}
        </>
      )}

    </Paper>
  )
}
