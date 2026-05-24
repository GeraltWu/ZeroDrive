import { Box, Text, UnstyledButton, useMantineTheme } from '@mantine/core'
import { useMediaQuery } from '@mantine/hooks'
import { IconFiles, IconHistory, IconLink } from '@tabler/icons-react'
import { useLocation, useNavigate } from 'react-router-dom'

const tools = [
  { path: '/', label: '文件', icon: IconFiles },
  { path: '/share-links', label: '分享', icon: IconLink },
  { path: '/access-logs', label: '记录', icon: IconHistory },
] as const

export function AppToolbar() {
  const theme = useMantineTheme()
  const isMobile = useMediaQuery(`(max-width: ${theme.breakpoints.sm})`) ?? false
  const { pathname } = useLocation()
  const navigate = useNavigate()

  if (isMobile) {
    return (
      <Box
        style={{
          flexShrink: 0,
          borderTop: '1px solid var(--mantine-color-default-border)',
          display: 'flex',
          justifyContent: 'space-around',
          alignItems: 'center',
          height: 56,
          backgroundColor: 'var(--mantine-color-body)',
        }}
      >
        {tools.map((t) => {
          const active = t.path === '/' ? pathname === '/' : pathname.startsWith(t.path)
          return (
            <UnstyledButton
              key={t.path}
              onClick={() => navigate(t.path)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 2,
                padding: '4px 12px',
                borderRadius: 8,
                color: active
                  ? 'var(--mantine-color-blue-6)'
                  : 'var(--mantine-color-gray-6)',
              }}
            >
              <t.icon size={22} stroke={active ? 2.2 : 1.6} />
              <Text component="span" fz={10} lh={1.2} fw={active ? 600 : 400}>
                {t.label}
              </Text>
            </UnstyledButton>
          )
        })}
      </Box>
    )
  }

  // Desktop: vertical left bar
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
