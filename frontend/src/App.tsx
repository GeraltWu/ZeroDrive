import { useEffect, useState } from 'react'
import { ActionIcon, Box, Burger, Button, Drawer, Group, NavLink, Title, useMantineColorScheme, useMantineTheme } from '@mantine/core'
import { useMediaQuery } from '@mantine/hooks'
import { BrowserRouter, Navigate, Outlet, Route, Routes, useLocation, useNavigate, useOutletContext } from 'react-router-dom'
import { IconFiles, IconHistory, IconLink, IconMoon, IconShield, IconSun } from '@tabler/icons-react'
import { AuthGuard } from './components/layout/AuthGuard'
import { AppToolbar } from './components/layout/AppToolbar'
import { DrivePage } from './pages/DrivePage'
import { LoginPage } from './pages/LoginPage'
import { PublicSharePage } from './pages/PublicSharePage'
import { RegisterPage } from './pages/RegisterPage'
import { AccessLogsPage } from './pages/AccessLogsPage'
import { AdminUsersPage } from './pages/AdminUsersPage'
import { ShareLinksPage } from './pages/ShareLinksPage'
import * as driveApi from './lib/driveApi'

export type AppContext = { isMobile: boolean; isAdmin: boolean; sidebarOpen: boolean; toggleSidebar: () => void }

export function useAppContext() { return useOutletContext<AppContext>() }

const navItems = [
  { path: '/', label: '我的文件', icon: IconFiles },
  { path: '/share-links', label: '分享链接', icon: IconLink },
  { path: '/access-logs', label: '访问记录', icon: IconHistory },
]

function AppLayout() {
  const { colorScheme, setColorScheme } = useMantineColorScheme()
  const theme = useMantineTheme()
  const isMobile = useMediaQuery(`(max-width: ${theme.breakpoints.sm})`) ?? false
  const dark = colorScheme === 'dark'
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [navOpen, setNavOpen] = useState(false)
  const [isAdmin, setIsAdmin] = useState(false)
  const toggleSidebar = () => setSidebarOpen((v) => !v)
  const { pathname } = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    driveApi.me().then((u) => setIsAdmin(u.is_admin)).catch(() => {})
  }, [])

  const allNav = isAdmin
    ? [...navItems, { path: '/admin/users', label: '用户管理', icon: IconShield }]
    : navItems

  const leftDrawerContent = (
    <Box>
      {allNav.map((t) => (
        <NavLink
          key={t.path}
          label={t.label}
          leftSection={<t.icon size={20} />}
          active={t.path === '/' ? pathname === '/' : pathname.startsWith(t.path)}
          onClick={() => { navigate(t.path); setNavOpen(false) }}
          style={{ borderRadius: 4 }}
        />
      ))}
      <Box mt="md" pt="md" style={{ borderTop: '1px solid var(--mantine-color-default-border)' }}>
        <Button
          fullWidth
          variant="subtle"
          color="red"
          size="xs"
          onClick={async () => {
            await driveApi.logout()
            window.location.href = '/login'
          }}
        >
          退出登录
        </Button>
      </Box>
    </Box>
  )

  return (
    <Box style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Shared header */}
      <Group
        h={56}
        px="md"
        justify="space-between"
        style={{
          borderBottom: '1px solid var(--mantine-color-default-border)',
          flexShrink: 0,
        }}
      >
        <Group gap="xs">
          {isMobile && (
            <Burger opened={navOpen} onClick={() => setNavOpen((v) => !v)} size="sm" />
          )}
          <Title order={4}>ZeroDrive</Title>
        </Group>
        <Group gap="xs">
          <ActionIcon
            variant="subtle"
            color="gray"
            onClick={() => setColorScheme(dark ? 'light' : 'dark')}
          >
            {dark ? <IconSun size={18} /> : <IconMoon size={18} />}
          </ActionIcon>
          {isMobile && (
            <Burger opened={sidebarOpen} onClick={toggleSidebar} size="sm" />
          )}
          {!isMobile && (
            <Button
              variant="subtle"
              size="xs"
              onClick={async () => {
                await driveApi.logout()
                window.location.href = '/login'
              }}
            >
              退出
            </Button>
          )}
        </Group>
      </Group>

      {/* Left nav drawer (mobile) */}
      {isMobile && (
        <Drawer
          opened={navOpen}
          onClose={() => setNavOpen(false)}
          size="xs"
          title="ZeroDrive"
          overlayProps={{ backgroundOpacity: 0.4 }}
        >
          {leftDrawerContent}
        </Drawer>
      )}

      {/* Toolbar + content */}
      <Box style={{ flex: '1 1 0%', display: 'flex', minHeight: 0, position: 'relative' }}>
        {!isMobile && <AppToolbar isAdmin={isAdmin} />}
        <Box
          style={{
            flex: '1 1 0%',
            minWidth: 0,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'auto',
          }}
        >
          <Outlet context={{ isMobile, isAdmin, sidebarOpen, toggleSidebar } satisfies AppContext} />
        </Box>
      </Box>
    </Box>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/s/:token" element={<PublicSharePage />} />
        <Route
          element={
            <AuthGuard>
              <AppLayout />
            </AuthGuard>
          }
        >
          <Route path="/" element={<DrivePage />} />
          <Route path="/share-links" element={<ShareLinksPage />} />
          <Route path="/access-logs" element={<AccessLogsPage />} />
          <Route path="/admin/users" element={<AdminUsersPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
