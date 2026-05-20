import { Box, Menu } from '@mantine/core'
import { IconCopy, IconInfoCircle, IconPencil, IconPlayerPlay, IconTrash, IconUpload } from '@tabler/icons-react'
import type { DriveNode } from '../../types/node'
import type { MediaPreviewKind } from '../../lib/mediaPreview'

export function DriveContextMenu({
  opened,
  x,
  y,
  selectedCount,
  targetNode,
  previewTarget,
  onOpenChange,
  onPreview,
  onDownload,
  onCopyLink,
  onCopyName,
  onProperties,
  onRename,
  onDelete,
  onBatchDelete,
}: {
  opened: boolean
  x: number
  y: number
  selectedCount: number
  targetNode: DriveNode | null
  previewTarget: { node: DriveNode; kind: MediaPreviewKind } | null
  onOpenChange: (opened: boolean) => void
  onPreview: (p: { node: DriveNode; kind: MediaPreviewKind }) => void
  onDownload: (node: DriveNode) => void
  onCopyLink: (node: DriveNode) => void
  onCopyName: (node: DriveNode) => void
  onProperties: (node: DriveNode) => void
  onRename: (node: DriveNode) => void
  onDelete: (node: DriveNode) => void
  onBatchDelete: () => void
}) {
  const showSingleNodeItems = targetNode !== null && selectedCount === 1
  const showBatchDelete = !showSingleNodeItems && selectedCount > 1
  const effectiveOpened = opened && (showSingleNodeItems || showBatchDelete)

  return (
    <Menu opened={effectiveOpened} onChange={onOpenChange} position="bottom-start" shadow="md">
      <Menu.Target>
        <Box
          style={{
            position: 'fixed',
            left: x,
            top: y,
            width: 1,
            height: 1,
            pointerEvents: 'none',
          }}
        />
      </Menu.Target>
      <Menu.Dropdown>
        {showSingleNodeItems && targetNode ? (
          <>
            {previewTarget && (
              <Menu.Item leftSection={<IconPlayerPlay size={14} />} onClick={() => onPreview(previewTarget)}>
                预览
              </Menu.Item>
            )}
            {!targetNode.is_folder && (
              <Menu.Item leftSection={<IconUpload size={14} />} onClick={() => onDownload(targetNode)}>
                下载
              </Menu.Item>
            )}
            {!targetNode.is_folder && (
              <Menu.Item leftSection={<IconCopy size={14} />} onClick={() => onCopyLink(targetNode)}>
                复制下载链接
              </Menu.Item>
            )}
            <Menu.Item leftSection={<IconCopy size={14} />} onClick={() => onCopyName(targetNode)}>
              复制文件名
            </Menu.Item>
            <Menu.Item leftSection={<IconInfoCircle size={14} />} onClick={() => onProperties(targetNode)}>
              属性
            </Menu.Item>
            <Menu.Item leftSection={<IconPencil size={14} />} onClick={() => onRename(targetNode)}>
              重命名
            </Menu.Item>
            <Menu.Item color="red" leftSection={<IconTrash size={14} />} onClick={() => onDelete(targetNode)}>
              删除
            </Menu.Item>
          </>
        ) : showBatchDelete ? (
          <Menu.Item color="red" leftSection={<IconTrash size={14} />} onClick={onBatchDelete}>
            删除已选（{selectedCount}）
          </Menu.Item>
        ) : null
        }
      </Menu.Dropdown>
    </Menu>
  )
}
