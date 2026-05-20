import { useState } from 'react'
import {
  Anchor,
  Button,
  Container,
  Paper,
  PasswordInput,
  Stack,
  Text,
  TextInput,
  Title,
} from '@mantine/core'
import { Link, useNavigate } from 'react-router-dom'
import * as driveApi from '../lib/driveApi'

export function LoginPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      await driveApi.login(username, password)
      navigate('/', { replace: true })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container size={420} my={80}>
      <Title ta="center">ZeroDrive</Title>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={handleSubmit}>
          <Stack>
            <TextInput
              label="用户名"
              placeholder="admin"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <PasswordInput
              label="密码"
              placeholder="在 .env 中配置"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Button type="submit" fullWidth loading={loading}>
              登录
            </Button>
          </Stack>
        </form>
      </Paper>
      <Text c="dimmed" size="sm" ta="center" mt="md">
        没有账号？<Anchor component={Link} to="/register">去注册</Anchor>
      </Text>
    </Container>
  )
}
