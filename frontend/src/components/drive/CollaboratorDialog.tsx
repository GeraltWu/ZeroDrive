import { useCallback, useEffect, useState } from 'react'
import {
  ActionIcon,
  Button,
  Group,
  Modal,
  Select,
  Stack,
  Table,
  Text,
  TextInput,
} from '@mantine/core'
import { IconTrash } from '@tabler/icons-react'
import * as driveApi from '../../lib/driveApi'
import type { Collaborator } from '../../types/node'

export function CollaboratorDialog({
  folderId,
  folderName,
  isOwner,
  opened,
  onClose,
}: {
  folderId: string
  folderName: string
  isOwner: boolean
  opened: boolean
  onClose: () => void
}) {
  const [items, setItems] = useState<Collaborator[]>([])
  const [username, setUsername] = useState('')
  const [role, setRole] = useState<string>('editor')
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => {
    void driveApi.listCollaborators(folderId).then(setItems)
  }, [folderId])

  useEffect(() => {
    if (opened) load()
  }, [opened, load])

  const handleAdd = async () => {
    if (!username.trim()) return
    setLoading(true)
    try {
      await driveApi.addCollaborator(folderId, username.trim(), role)
      setUsername('')
      load()
    } catch {
      // error shown by interceptor
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = async (userId: string) => {
    try {
      await driveApi.removeCollaborator(folderId, userId)
      load()
    } catch {
      // error shown by interceptor
    }
  }

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await driveApi.updateCollaborator(folderId, userId, newRole)
      load()
    } catch {
      // error shown by interceptor
    }
  }

  return (
    <Modal opened={opened} onClose={onClose} title={`协作管理 — ${folderName}`} size="lg" centered>
      <Stack>
        {isOwner && (
          <Group gap="sm" wrap="nowrap" align="end">
            <TextInput
              placeholder="输入用户名"
              value={username}
              onChange={(e) => setUsername(e.currentTarget.value)}
              style={{ flex: 1 }}
            />
            <Select
              data={[
                { value: 'viewer', label: '只读' },
                { value: 'editor', label: '编辑' },
                { value: 'admin', label: '管理' },
              ]}
              value={role}
              onChange={(v) => v && setRole(v)}
              w={100}
            />
            <Button onClick={() => void handleAdd()} loading={loading}>
              邀请
            </Button>
          </Group>
        )}

        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>用户名</Table.Th>
              <Table.Th w={100}>角色</Table.Th>
              <Table.Th w={60} />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {items.length === 0 ? (
              <Table.Tr>
                <Table.Td colSpan={3}>
                  <Text size="sm" c="dimmed" ta="center">
                    暂无协作者
                  </Text>
                </Table.Td>
              </Table.Tr>
            ) : (
              items.map((c) => (
                <Table.Tr key={c.id}>
                  <Table.Td>{c.username}</Table.Td>
                  <Table.Td>
                    {isOwner ? (
                      <Select
                        data={[
                          { value: 'viewer', label: '只读' },
                          { value: 'editor', label: '编辑' },
                          { value: 'admin', label: '管理' },
                        ]}
                        value={c.role}
                        onChange={(v) => v && handleRoleChange(c.user_id, v)}
                        size="xs"
                      />
                    ) : (
                      <Text size="sm">
                        {c.role === 'viewer' ? '只读' : c.role === 'editor' ? '编辑' : '管理'}
                      </Text>
                    )}
                  </Table.Td>
                  <Table.Td>
                    {isOwner && (
                      <ActionIcon
                        variant="subtle"
                        color="red"
                        size="sm"
                        onClick={() => void handleRemove(c.user_id)}
                      >
                        <IconTrash size={14} />
                      </ActionIcon>
                    )}
                  </Table.Td>
                </Table.Tr>
              ))
            )}
          </Table.Tbody>
        </Table>
      </Stack>
    </Modal>
  )
}
