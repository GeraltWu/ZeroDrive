import { useEffect, useState, type ReactNode } from 'react'
import { Center, Loader } from '@mantine/core'
import { useNavigate } from 'react-router-dom'
import * as driveApi from '../../lib/driveApi'
import { getAccessToken } from '../../lib/api'

export function AuthGuard({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const [ok, setOk] = useState<boolean | null>(null)

  useEffect(() => {
    let cancelled = false
    if (!getAccessToken()) {
      setOk(false)
      navigate('/login', { replace: true })
      return
    }
    ;(async () => {
      try {
        await driveApi.me()
        if (!cancelled) setOk(true)
      } catch {
        if (!cancelled) {
          setOk(false)
          navigate('/login', { replace: true })
        }
      }
    })()
    return () => {
      cancelled = true
    }
  }, [navigate])

  if (ok !== true) {
    return (
      <Center h="100%">
        <Loader />
      </Center>
    )
  }

  return children
}
