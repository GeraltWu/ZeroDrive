import { useMemo, useState } from 'react'
import { ActionIcon, Anchor, Box, Group, Menu, Paper, Text, Tooltip } from '@mantine/core'
import { IconArrowUp, IconChevronLeft, IconChevronRight, IconDots, IconRefresh } from '@tabler/icons-react'
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
    data: { dropType: 'breadcrumb' as const },
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
        whiteSpace: 'nowrap',
      }}
    >
      {label}
    </Anchor>
  )
}

function CrumbOverflowMenu({
  items,
  crumbs,
  rootId,
  crumbLabel,
  onSegment,
  draggingId,
}: {
  items: BreadcrumbItem[]
  crumbs: BreadcrumbItem[]
  rootId: string
  crumbLabel: (c: BreadcrumbItem, rootId: string) => string
  onSegment: (index: number) => void
  draggingId: string | null
}) {
  const [opened, setOpened] = useState(false)

  return (
    <Menu opened={opened} onChange={setOpened} shadow="md" position="bottom-start">
      <Menu.Target>
        <Anchor
          size="sm"
          c="dimmed"
          style={{ borderRadius: 6, padding: '2px 4px', whiteSpace: 'nowrap' }}
          onClick={() => setOpened(true)}
        >
          <IconDots size={14} style={{ verticalAlign: -2 }} />
        </Anchor>
      </Menu.Target>
      <Menu.Dropdown>
        {items.map((c) => {
          const i = crumbs.indexOf(c)
          return (
            <Menu.Item
              key={c.id}
              onClick={() => {
                setOpened(false)
                onSegment(i)
              }}
            >
              <Text size="sm">{crumbLabel(c, rootId)}</Text>
            </Menu.Item>
          )
        })}
      </Menu.Dropdown>
    </Menu>
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
  maxVisible = 4,
  isMobile = false,
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
  maxVisible?: number
  isMobile?: boolean
}) {
  const { visible, collapsed } = useMemo(() => {
    if (crumbs.length <= maxVisible) {
      return { visible: crumbs, collapsed: [] as BreadcrumbItem[] }
    }
    const lastN = Math.max(1, maxVisible - 2)
    return {
      visible: [crumbs[0]!, ...crumbs.slice(-lastN)],
      collapsed: crumbs.slice(1, -lastN || undefined),
    }
  }, [crumbs, maxVisible])

  const btnGroup = (
    <>
      <Tooltip label="后退">
        <ActionIcon variant="default" size="lg" disabled={!canBack} onClick={onBack} aria-label="后退">
          <IconChevronLeft size={18} />
        </ActionIcon>
      </Tooltip>
      <Tooltip label="前进">
        <ActionIcon variant="default" size="lg" disabled={!canForward} onClick={onForward} aria-label="前进">
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
    </>
  )

  const crumbRow = (
    <Box style={{ flex: 1, minWidth: 0, overflow: 'hidden' }}>
      <Group wrap="nowrap" gap={2}>
        {visible.map((c, vi) => {
          const origIdx = crumbs.indexOf(c)
          return (
                <Group key={c.id} wrap="nowrap" gap={2}>
                  {vi === 1 && collapsed.length > 0 && (
                    <>
                      <CrumbOverflowMenu
                        items={collapsed}
                        crumbs={crumbs}
                        rootId={rootId}
                        crumbLabel={crumbLabel}
                        onSegment={onBreadcrumbSegment}
                        draggingId={draggingNodeId}
                      />
                      <Text span size="sm" c="dimmed">
                        ›
                      </Text>
                    </>
                  )}
                  <BreadcrumbDropSegment
                    id={c.id}
                    label={crumbLabel(c, rootId)}
                    active={origIdx === crumbs.length - 1}
                    onClick={() => onBreadcrumbSegment(origIdx)}
                    disabledDrop={draggingNodeId === c.id}
                  />
                  {vi < visible.length - 1 && (
                    <Text span size="sm" c="dimmed">
                      ›
                    </Text>
                  )}
                </Group>
              )
            })}
          </Group>
        </Box>
    )

  return (
    <Paper withBorder p="sm" mb="xs" bg="var(--mantine-color-body)">
      {isMobile ? (
        <Box>
          <Group wrap="nowrap" gap="xs" mb={6}>
            {btnGroup}
          </Group>
          {crumbRow}
        </Box>
      ) : (
        <Group wrap="nowrap" gap="xs" align="center">
          {btnGroup}
          {crumbRow}
        </Group>
      )}
    </Paper>
  )
}
