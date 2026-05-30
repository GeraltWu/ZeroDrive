import { Box, Text, UnstyledButton } from '@mantine/core'
import { IconFiles, IconHistory, IconLink, IconShield } from '@tabler/icons-react'
import { useLocation, useNavigate } from 'react-router-dom'

function buildTools(isAdmin: boolean) {
  const base = [
    { path: '/', label: '文件', icon: IconFiles },
    { path: '/share-links', label: '分享', icon: IconLink },
    { path: '/access-logs', label: '记录', icon: IconHistory },
  ] as const
  if (isAdmin) {
    return [...base, { path: '/admin/users' as const, label: '管理', icon: IconShield }]
  }
  return base
}

export function AppToolbar({ isAdmin = false }: { isAdmin?: boolean }) {
  const tools = buildTools(isAdmin)
  const { pathname } = useLocation()
  const navigate = useNavigate()

  return (
    <Box
      style={{
        width: 64,
        flexShrink: 0,
        borderRight: '1px solid var(--mantine-color-default-border)',
        backgroundColor: 'var(--mantine-color-body)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        paddingTop: 12,
        gap: 2,
      }}
    >
      {tools.map((t) => {
        const active =
          t.path === '/' ? pathname === '/' : pathname.startsWith(t.path)
        return (
          <UnstyledButton
            key={t.path}
            onClick={() => navigate(t.path)}
            style={{
              width: 52,
              padding: '8px 4px 6px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 3,
              borderRadius: 8,
              backgroundColor: active
                ? 'var(--mantine-color-blue-light)'
                : 'transparent',
              color: active
                ? 'var(--mantine-color-blue-6)'
                : 'var(--mantine-color-gray-6)',
              transition: 'background-color 120ms ease, color 120ms ease',
            }}
          >
            <t.icon size={24} stroke={active ? 2.2 : 1.6} />
            <Text component="span" fz={10} lh={1.2} fw={active ? 600 : 400}>
              {t.label}
            </Text>
          </UnstyledButton>
        )
      })}
    </Box>
  )
}
