import { Modal } from '@mantine/core'
import * as driveApi from '../../lib/driveApi'
import type { DriveNode } from '../../types/node'
import type { MediaPreviewKind } from '../../lib/mediaPreview'

export function MediaPreviewModal({
  preview,
  onClose,
}: {
  preview: { node: DriveNode; kind: MediaPreviewKind } | null
  onClose: () => void
}) {
  return (
    <Modal
      opened={preview !== null}
      onClose={onClose}
      title={preview?.node.name ?? '预览'}
      size="xl"
      centered
      zIndex={500}
    >
      {preview?.kind === 'video' && (
        <video
          key={preview.node.id}
          controls
          playsInline
          src={driveApi.downloadUrl(preview.node.id)}
          style={{
            width: '100%',
            maxHeight: '72vh',
            background: 'var(--mantine-color-dark-9)',
          }}
        />
      )}
      {preview?.kind === 'image' && (
        <img
          key={preview.node.id}
          src={driveApi.downloadUrl(preview.node.id)}
          alt={preview.node.name}
          style={{
            width: '100%',
            maxHeight: '72vh',
            objectFit: 'contain',
          }}
        />
      )}
      {preview?.kind === 'audio' && (
        <audio
          key={preview.node.id}
          controls
          src={driveApi.downloadUrl(preview.node.id)}
          style={{ width: '100%' }}
        />
      )}
    </Modal>
  )
}
