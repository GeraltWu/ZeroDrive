import { useCallback, useEffect, useState } from 'react'
import {
  ActionIcon,
  Badge,
  Box,
  CopyButton,
  Group,
  Table,
  Text,
  Title,
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { IconCheck, IconCopy, IconPlayerPause, IconPlayerPlay, IconTrash } from '@tabler/icons-react'
import * as driveApi from '../lib/driveApi'
import type { ShareLinkWithNode } from '../types/node'

export function ShareLinksPage() {
  const [links, setLinks] = useState<ShareLinkWithNode[]>([])

  const load = useCallback(() => {
    driveApi.listAllShareLinks().then(setLinks).catch(() => {})
  }, [])

  useEffect(() => { load() }, [load])

  const handleToggle = async (linkId: string) => {
    try {
      await driveApi.toggleShareLink(linkId)
      load()
    } catch { /* handled by interceptor */ }
  }

  const handleRevoke = async (linkId: string) => {
    try {
      await driveApi.revokeShareLink(linkId)
      load()
      notifications.show({ color: 'green', message: '分享链接已撤销' })
    } catch { /* handled by interceptor */ }
  }

  const formatExpire = (d: string | null) => {
    if (!d) return '永不过期'
    return new Date(d).toLocaleString()
  }

  return (
    <Box p="md" style={{ flex: 1, overflow: 'auto' }}>
      <Title order={4} mb="md">
        分享链接管理
      </Title>

      {links.length === 0 ? (
        <Text size="sm" c="dimmed" ta="center" py="xl">
          暂无分享链接。在文件或文件夹上右键 →「分享」创建。
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
              <Table.Th>文件 / 文件夹</Table.Th>
              <Table.Th>链接</Table.Th>
              <Table.Th>密码</Table.Th>
              <Table.Th>过期时间</Table.Th>
              <Table.Th>访问次数</Table.Th>
              <Table.Th w={100}>状态</Table.Th>
              <Table.Th w={80}>操作</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {links.map((link) => (
              <Table.Tr key={link.id} opacity={link.is_active ? 1 : 0.5}>
                <Table.Td>
                  <Text truncate maw={220}>
                    {link.node_name}
                  </Text>
                </Table.Td>
                <Table.Td>
                  <Group gap={4} wrap="nowrap">
                    <Text truncate maw={130}>
                      /s/{link.token.slice(0, 10)}…
                    </Text>
                    <CopyButton value={driveApi.absoluteShareUrl(link.token)}>
                      {({ copied, copy }) => (
                        <ActionIcon size="sm" variant="subtle" color={copied ? 'teal' : 'gray'} onClick={copy}>
                          {copied ? <IconCheck size={14} /> : <IconCopy size={14} />}
                        </ActionIcon>
                      )}
                    </CopyButton>
                  </Group>
                </Table.Td>
                <Table.Td>{link.has_password ? '是' : '否'}</Table.Td>
                <Table.Td>{formatExpire(link.expire_at)}</Table.Td>
                <Table.Td>
                  {link.max_access_count === null
                    ? `${link.access_count} 次`
                    : `${link.access_count} / ${link.max_access_count} 次`}
                </Table.Td>
                <Table.Td>
                  <Badge color={link.is_active ? 'teal' : 'red'} variant="light">
                    {link.is_active ? '生效中' : '已停用'}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Group gap={4}>
                    <ActionIcon size="sm" variant="subtle" color={link.is_active ? 'yellow' : 'teal'} onClick={() => handleToggle(link.id)}>
                      {link.is_active ? <IconPlayerPause size={14} /> : <IconPlayerPlay size={14} />}
                    </ActionIcon>
                    <ActionIcon size="sm" variant="subtle" color="red" onClick={() => handleRevoke(link.id)}>
                      <IconTrash size={14} />
                    </ActionIcon>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}
    </Box>
  )
}
