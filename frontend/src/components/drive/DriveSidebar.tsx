import { useEffect, useState } from 'react'
import { Divider, NavLink, Paper, Text } from '@mantine/core'
import { IconFolder } from '@tabler/icons-react'
import { FolderTree } from './FolderTree'
import * as driveApi from '../../lib/driveApi'
import type { FolderTreeItem, SharedFolder } from '../../types/node'

export function DriveSidebar({
  flatFolders,
  rootId,
  folderId,
  onTreeSelect,
  draggingNodeId,
}: {
  flatFolders: FolderTreeItem[]
  rootId: string | null
  folderId: string | null
  onTreeSelect: (id: string) => void
  draggingNodeId: string | null
}) {
  const [sharedFolders, setSharedFolders] = useState<SharedFolder[]>([])

  useEffect(() => {
    void driveApi.listSharedWithMe().then(setSharedFolders)
  }, [])

  if (!rootId) return null

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
              description={sf.role === 'viewer' ? '只读' : sf.role === 'editor' ? '可编辑' : '管理员'}
              style={{ borderRadius: 4 }}
            />
          ))}
        </>
      )}
    </Paper>
  )
}
