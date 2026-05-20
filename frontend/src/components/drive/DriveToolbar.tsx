import { ActionIcon, Anchor, Box, Breadcrumbs, Group, Paper, Tooltip } from '@mantine/core'
import { IconArrowUp, IconChevronLeft, IconChevronRight, IconRefresh } from '@tabler/icons-react'
import { useDroppable } from '@dnd-kit/core'
import type { BreadcrumbItem } from '../../types/node'

function BreadcrumbDropSegment({
  id,
  label,
  active,
  onClick,
  disabledDrop,
}: {
  id: string
  label: string
  active: boolean
  onClick: () => void
  disabledDrop: boolean
}) {
  const { setNodeRef: setDropNodeRef, isOver: isDropOver } = useDroppable({
    id: `crumb-folder:${id}`,
    disabled: disabledDrop,
    data: {
      dropType: 'breadcrumb' as const,
    },
  })

  return (
    <Anchor
      ref={setDropNodeRef}
      size="sm"
      onClick={onClick}
      c={active ? 'dimmed' : 'blue'}
      style={{
        pointerEvents: active ? 'none' : undefined,
        borderRadius: 6,
        padding: '2px 4px',
        backgroundColor: isDropOver ? 'var(--mantine-color-blue-light)' : undefined,
      }}
    >
      {label}
    </Anchor>
  )
}

export function DriveToolbar({
  canBack,
  canForward,
  canUp,
  onBack,
  onForward,
  onUp,
  onRefresh,
  crumbs,
  rootId,
  onBreadcrumbSegment,
  crumbLabel,
  draggingNodeId,
}: {
  canBack: boolean
  canForward: boolean
  canUp: boolean
  onBack: () => void
  onForward: () => void
  onUp: () => void
  onRefresh: () => void
  crumbs: BreadcrumbItem[]
  rootId: string
  onBreadcrumbSegment: (segmentIndex: number) => void
  crumbLabel: (c: BreadcrumbItem, rootId: string) => string
  draggingNodeId: string | null
}) {
  return (
    <Paper withBorder p="sm" mb="xs" bg="var(--mantine-color-body)">
      <Group wrap="nowrap" gap="xs" align="center">
        <Tooltip label="后退">
          <ActionIcon variant="default" size="lg" disabled={!canBack} onClick={onBack} aria-label="后退">
            <IconChevronLeft size={18} />
          </ActionIcon>
        </Tooltip>
        <Tooltip label="前进">
          <ActionIcon
            variant="default"
            size="lg"
            disabled={!canForward}
            onClick={onForward}
            aria-label="前进"
          >
            <IconChevronRight size={18} />
          </ActionIcon>
        </Tooltip>
        <Tooltip label="上级文件夹">
          <ActionIcon variant="default" size="lg" disabled={!canUp} onClick={onUp} aria-label="向上">
            <IconArrowUp size={18} />
          </ActionIcon>
        </Tooltip>
        <Tooltip label="刷新">
          <ActionIcon variant="default" size="lg" onClick={onRefresh} aria-label="刷新">
            <IconRefresh size={18} />
          </ActionIcon>
        </Tooltip>
        <Box style={{ flex: 1, minWidth: 0 }}>
          <Breadcrumbs
            styles={{
              root: { flexWrap: 'nowrap', overflow: 'hidden' },
              breadcrumb: { textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' },
            }}
            separator="›"
          >
            {crumbs.map((c, i) => (
              <BreadcrumbDropSegment
                key={c.id}
                id={c.id}
                label={crumbLabel(c, rootId)}
                active={i === crumbs.length - 1}
                onClick={() => onBreadcrumbSegment(i)}
                disabledDrop={draggingNodeId === c.id}
              />
            ))}
          </Breadcrumbs>
        </Box>
      </Group>
    </Paper>
  )
}
