import { Paper, Text } from '@mantine/core'
import { FolderTree } from './FolderTree'
import type { FolderTreeItem } from '../../types/node'

export function DriveSidebar({
  flatFolders,
  rootId,
  folderId,
  onTreeSelect,
  draggingNodeId,
}: {
  flatFolders: FolderTreeItem[]
  rootId: string
  folderId: string
  onTreeSelect: (id: string) => void
  draggingNodeId: string | null
}) {
  return (
    <Paper withBorder p={6} w={300} miw={300} maw={300} style={{ flexShrink: 0 }}>
      <Text size="xs" c="dimmed" mb="xs" fw={600}>
        文件夹
      </Text>
      <FolderTree
        flat={flatFolders}
        rootId={rootId}
        selectedId={folderId}
        onSelect={(id) => void onTreeSelect(id)}
        draggingNodeId={draggingNodeId}
      />
    </Paper>
  )
}
