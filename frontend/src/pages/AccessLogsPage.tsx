import { useCallback, useEffect, useState } from 'react'
import { Box, Table, Text, Title } from '@mantine/core'
import { IconDownload, IconFolderPlus } from '@tabler/icons-react'
import * as driveApi from '../lib/driveApi'
import type { AccessLog } from '../types/node'

function formatBytes(n: number | null): string {
  if (n === null) return ''
  if (n < 1024) return `${n} B`
  const u = ['KB', 'MB', 'GB']
  let v = n / 1024
  let i = 0
  while (v >= 1024 && i < u.length - 1) {
    v /= 1024
    i += 1
  }
  return `${v.toFixed(1)} ${u[i]}`
}

function describe(log: AccessLog): string {
  const user = log.visitor_name || '匿名用户'
  const node = log.node_name
  if (log.action === 'join') return `${user} 加入了「${node}」`
  return `${user} 下载了「${node}」`
}

const actionIcons: Record<string, typeof IconDownload> = {
  download: IconDownload,
  join: IconFolderPlus,
}

export function AccessLogsPage() {
  const [logs, setLogs] = useState<AccessLog[]>([])

  const load = useCallback(() => {
    driveApi.listAccessLogs().then(setLogs).catch(() => {})
  }, [])

  useEffect(() => { load() }, [load])

  return (
    <Box p="md" style={{ flex: 1, overflow: 'auto' }}>
      <Title order={4} mb="md">
        访问记录
      </Title>

      {logs.length === 0 ? (
        <Text size="sm" c="dimmed" ta="center" py="xl">
          暂无访问记录。当有人通过分享链接下载或加入文件夹时显示。
        </Text>
      ) : (
        <Table
          striped
          highlightOnHover
          withTableBorder
          withColumnBorders
          style={{ width: '100%', tableLayout: 'auto' }}
        >
          <Table.Thead>
            <Table.Tr>
              <Table.Th>时间</Table.Th>
              <Table.Th>操作</Table.Th>
              <Table.Th>文件</Table.Th>
              <Table.Th>大小</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {logs.map((log) => {
              const Icon = actionIcons[log.action] ?? IconDownload
              return (
                <Table.Tr key={log.id}>
                  <Table.Td>{new Date(log.created_at).toLocaleString()}</Table.Td>
                  <Table.Td>
                    <Text size="sm">
                      <Icon size={14} style={{ verticalAlign: -2, marginRight: 4 }} />
                      {describe(log)}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{log.node_name}</Text>
                  </Table.Td>
                  <Table.Td>
                    {log.size != null ? formatBytes(log.size) : '—'}
                  </Table.Td>
                </Table.Tr>
              )
            })}
          </Table.Tbody>
        </Table>
      )}
    </Box>
  )
}
