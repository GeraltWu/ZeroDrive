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
import { notifications } from '@mantine/notifications'
import { Link, useNavigate } from 'react-router-dom'
import * as driveApi from '../lib/driveApi'

export function RegisterPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (password !== confirm) {
      notifications.show({ color: 'red', title: '两次密码不一致', message: '请重新输入' })
      return
    }
    setLoading(true)
    try {
      await driveApi.register(username, password)
      notifications.show({ color: 'green', title: '注册成功', message: '请登录' })
      navigate('/login', { replace: true })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container size={420} my={80}>
      <Title ta="center">注册 ZeroDrive</Title>
      <Text c="dimmed" size="sm" ta="center" mt={5}>
        创建新账号
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={handleSubmit}>
          <Stack>
            <TextInput
              label="用户名"
              placeholder="3～64 位"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
              maxLength={64}
            />
            <PasswordInput
              label="密码"
              placeholder="6～128 位"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              maxLength={128}
            />
            <PasswordInput
              label="确认密码"
              placeholder="再次输入密码"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
            />
            <Button type="submit" fullWidth loading={loading}>
              注册
            </Button>
          </Stack>
        </form>
      </Paper>
      <Text c="dimmed" size="sm" ta="center" mt="md">
        已有账号？<Anchor component={Link} to="/login">登录</Anchor>
      </Text>
    </Container>
  )
}
