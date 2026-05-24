import { useState } from 'react'
import { ActionIcon, Box, Burger, Button, Group, Title, useMantineColorScheme, useMantineTheme } from '@mantine/core'
import { useMediaQuery } from '@mantine/hooks'
import { BrowserRouter, Navigate, Outlet, Route, Routes, useOutletContext } from 'react-router-dom'
import { IconMoon, IconSun } from '@tabler/icons-react'
import { AuthGuard } from './components/layout/AuthGuard'
import { AppToolbar } from './components/layout/AppToolbar'
import { DrivePage } from './pages/DrivePage'
import { LoginPage } from './pages/LoginPage'
import { PublicSharePage } from './pages/PublicSharePage'
import { RegisterPage } from './pages/RegisterPage'
import { AccessLogsPage } from './pages/AccessLogsPage'
import { ShareLinksPage } from './pages/ShareLinksPage'
import * as driveApi from './lib/driveApi'

export type AppContext = { isMobile: boolean; sidebarOpen: boolean; toggleSidebar: () => void }

export function useAppContext() { return useOutletContext<AppContext>() }

function AppLayout() {
  const { colorScheme, setColorScheme } = useMantineColorScheme()
  const theme = useMantineTheme()
  const isMobile = useMediaQuery(`(max-width: ${theme.breakpoints.sm})`) ?? false
  const dark = colorScheme === 'dark'
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const toggleSidebar = () => setSidebarOpen((v) => !v)

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
            <Burger opened={sidebarOpen} onClick={toggleSidebar} size="sm" />
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

      {/* Toolbar + content */}
      <Box style={{ flex: '1 1 0%', display: 'flex', minHeight: 0, position: 'relative' }}>
        {!isMobile && <AppToolbar />}
        <Box
          style={{
            flex: '1 1 0%',
            minWidth: 0,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'auto',
          }}
        >
          <Outlet context={{ isMobile, sidebarOpen, toggleSidebar } satisfies AppContext} />
        </Box>
      </Box>

      {/* Mobile bottom toolbar */}
      {isMobile && <AppToolbar />}
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
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
