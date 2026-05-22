import { type ReactNode, useState } from 'react'
import { ActionIcon, Box, Button, Group, Menu, Table, Text } from '@mantine/core'
import {
  IconArrowDown,
  IconArrowUp,
  IconArrowsSort,
  IconCheck,
  IconFolderPlus,
  IconLayoutGrid,
  IconList,
  IconUpload,
  IconUsers,
} from '@tabler/icons-react'

export type ViewMode = 'list' | 'small' | 'large'
export type SortKey = 'name' | 'size' | 'updated_at'
export type SortDir = 'asc' | 'desc'

const viewModeLabels: Record<ViewMode, string> = {
  list: '列表',
  small: '小图标',
  large: '大图标',
}

const sortLabels: Record<SortKey, string> = {
  name: '名称',
  size: '大小',
  updated_at: '修改时间',
}

function ViewModeIcon({ mode }: { mode: ViewMode }) {
  if (mode === 'list') return <IconList size={20} />
  return <IconLayoutGrid size={20} />
}

function SortableTh({
  field,
  label,
  w,
  sortKey,
  sortDir,
  onSort,
}: {
  field: SortKey
  label: string
  w?: number
  sortKey: SortKey
  sortDir: SortDir
  onSort: (key: SortKey) => void
}) {
  const [hovered, setHovered] = useState(false)
  const active = sortKey === field
  return (
    <Table.Th
      w={w}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        cursor: 'pointer',
        backgroundColor: hovered ? 'var(--mantine-color-blue-0)' : undefined,
        transition: 'background-color 150ms ease',
      }}
      onClick={() => onSort(field)}
    >
      <Group gap={4} wrap="nowrap">
        <Text span inherit>
          {label}
        </Text>
        {active && (
          sortDir === 'asc' ? <IconArrowUp size={14} /> : <IconArrowDown size={14} />
        )}
      </Group>
    </Table.Th>
  )
}

export function DriveContentPane({
  uploading,
  uploadProgress,
  viewMode,
  onViewModeChange,
  sortKey,
  sortDir,
  onSortChange,
  onNewFolder,
  onPickFiles,
  isOwnFolder,
  onManageCollaborators,
  tableBody,
  gridBody,
  contextMenu,
}: {
  uploading: boolean
  uploadProgress: { done: number; total: number }
  viewMode: ViewMode
  onViewModeChange: (mode: ViewMode) => void
  sortKey: SortKey
  sortDir: SortDir
  onSortChange: (key: SortKey) => void
  onNewFolder: () => void
  onPickFiles: (files: FileList | null) => void
  isOwnFolder: boolean
  onManageCollaborators: () => void
  tableBody: ReactNode
  gridBody: ReactNode
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
          {isOwnFolder && (
            <Button leftSection={<IconUsers size={18} />} variant="subtle" onClick={onManageCollaborators}>
              协作
            </Button>
          )}
          <Menu shadow="md" width={140}>
            <Menu.Target>
              <ActionIcon variant="subtle" size="lg">
                <ViewModeIcon mode={viewMode} />
              </ActionIcon>
            </Menu.Target>
            <Menu.Dropdown>
              {(['list', 'small', 'large'] as ViewMode[]).map((mode) => (
                <Menu.Item
                  key={mode}
                  leftSection={<ViewModeIcon mode={mode} />}
                  rightSection={viewMode === mode ? <IconCheck size={14} /> : undefined}
                  onClick={() => onViewModeChange(mode)}
                >
                  {viewModeLabels[mode]}
                </Menu.Item>
              ))}
            </Menu.Dropdown>
          </Menu>
          <Menu shadow="md" width={140}>
            <Menu.Target>
              <ActionIcon variant="subtle" size="lg">
                <IconArrowsSort size={20} />
              </ActionIcon>
            </Menu.Target>
            <Menu.Dropdown>
              {(Object.entries(sortLabels) as [SortKey, string][]).map(([key, label]) => (
                <Menu.Item
                  key={key}
                  rightSection={
                    sortKey === key ? (
                      sortDir === 'asc' ? <IconArrowUp size={14} /> : <IconArrowDown size={14} />
                    ) : undefined
                  }
                  onClick={() => onSortChange(key)}
                >
                  {label}
                </Menu.Item>
              ))}
            </Menu.Dropdown>
          </Menu>
        </Group>
        <Group gap="sm">
          <Text size="sm" c="dimmed">
            {uploading
              ? `正在上传（${uploadProgress.done}/${uploadProgress.total}）`
              : '可将文件拖入此页任意区域上传至当前文件夹。'}
          </Text>
        </Group>
      </Group>

      {viewMode === 'list' ? (
        <Table
          striped
          highlightOnHover
          withTableBorder
          withColumnBorders
          style={{ width: '100%', tableLayout: 'auto' }}
        >
          <Table.Thead>
            <Table.Tr>
              <SortableTh field="name" label="名称" sortKey={sortKey} sortDir={sortDir} onSort={onSortChange} />
              <SortableTh field="size" label="大小" w={100} sortKey={sortKey} sortDir={sortDir} onSort={onSortChange} />
              <SortableTh field="updated_at" label="修改时间" w={180} sortKey={sortKey} sortDir={sortDir} onSort={onSortChange} />
              <Table.Th w={100}>下载</Table.Th>
              <Table.Th w={60} />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>{tableBody}</Table.Tbody>
        </Table>
      ) : (
        gridBody
      )}

      {contextMenu}
    </Box>
  )
}
