import { useEffect, useRef, useState } from 'react'
import { Modal } from '@mantine/core'
import * as driveApi from '../../lib/driveApi'
import type { DriveNode } from '../../types/node'
import type { MediaPreviewKind } from '../../lib/mediaPreview'

interface PreviewData {
  node: DriveNode
  kind: MediaPreviewKind
}

export function MediaPreviewModal({
  preview,
  onClose,
}: {
  preview: PreviewData | null
  onClose: () => void
}) {
  const [cached, setCached] = useState<PreviewData | null>(null)
  const timerRef = useRef<ReturnType<typeof setTimeout>>()

  useEffect(() => {
    if (preview) {
      clearTimeout(timerRef.current)
      setCached(preview)
    } else if (cached) {
      // 等退出动画结束后再清空，避免闪现空窗口
      timerRef.current = setTimeout(() => setCached(null), 200)
    }
    return () => clearTimeout(timerRef.current)
  }, [preview])

  const active = cached

  return (
    <Modal
      opened={preview !== null}
      onClose={onClose}
      title={active?.node.name ?? ''}
      size="xl"
      centered
      zIndex={500}
    >
      {active?.kind === 'video' && (
        <video
          key={active.node.id}
          controls
          playsInline
          src={driveApi.downloadUrl(active.node.id)}
          style={{
            width: '100%',
            maxHeight: '72vh',
            background: 'var(--mantine-color-dark-9)',
          }}
        />
      )}
      {active?.kind === 'image' && (
        <img
          key={active.node.id}
          src={driveApi.downloadUrl(active.node.id)}
          alt={active.node.name}
          style={{
            width: '100%',
            maxHeight: '72vh',
            objectFit: 'contain',
          }}
        />
      )}
      {active?.kind === 'audio' && (
        <audio
          key={active.node.id}
          controls
          src={driveApi.downloadUrl(active.node.id)}
          style={{ width: '100%' }}
        />
      )}
    </Modal>
  )
}
