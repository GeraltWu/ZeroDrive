import type { ReactNode } from 'react'
import { Box, Button, Group, Table, Text } from '@mantine/core'
import { IconFolderPlus, IconUpload } from '@tabler/icons-react'

export function DriveContentPane({
  uploading,
  uploadProgress,
  onNewFolder,
  onPickFiles,
  tableBody,
  contextMenu,
}: {
  uploading: boolean
  uploadProgress: { done: number; total: number }
  onNewFolder: () => void
  onPickFiles: (files: FileList | null) => void
  tableBody: ReactNode
  contextMenu: ReactNode
}) {
  return (
    <Box style={{ flex: '1 1 0%', minWidth: 0, alignSelf: 'stretch' }}>
      <Group justify="space-between" wrap="wrap" mb="sm" gap="sm">
        <Group gap="sm">
          <Button leftSection={<IconFolderPlus size={18} />} variant="light" onClick={onNewFolder}>
            新建文件夹
          </Button>
          <Button component="label" htmlFor="file-up" leftSection={<IconUpload size={18} />} loading={uploading}>
            上传
          </Button>
          <input id="file-up" type="file" multiple hidden onChange={(e) => onPickFiles(e.target.files)} />
        </Group>
        <Text size="sm" c="dimmed">
          {uploading
            ? `正在上传（${uploadProgress.done}/${uploadProgress.total}）`
            : '可将文件拖入此页任意区域上传至当前文件夹。'}
        </Text>
      </Group>
      <Table
        striped
        highlightOnHover
        withTableBorder
        withColumnBorders
        style={{ width: '100%', tableLayout: 'auto' }}
      >
        <Table.Thead>
          <Table.Tr>
            <Table.Th>名称</Table.Th>
            <Table.Th w={100}>大小</Table.Th>
            <Table.Th w={180}>修改时间</Table.Th>
            <Table.Th w={100}>下载</Table.Th>
            <Table.Th w={60} />
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{tableBody}</Table.Tbody>
      </Table>
      {contextMenu}
    </Box>
  )
}
