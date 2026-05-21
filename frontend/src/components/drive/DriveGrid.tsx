import { useState } from 'react'
import { Box, Image, Paper, SimpleGrid, Text } from '@mantine/core'
import type { DriveNode } from '../../types/node'
import { FileTypeIcon, IMAGE } from '../../lib/fileTypeIcon'
import * as driveApi from '../../lib/driveApi'

function isImageFilename(name: string): boolean {
  const i = name.lastIndexOf('.')
  if (i <= 0 || i >= name.length - 1) return false
  return IMAGE.has(name.slice(i + 1).toLowerCase())
}

type GridSize = 'small' | 'large'

const gridLayout: Record<GridSize, { cols: Record<string, number>; iconSize: number; thumbSize: number }> = {
  small: { cols: { base: 4, xs: 5, sm: 6, md: 8, lg: 10 }, iconSize: 28, thumbSize: 200 },
  large: { cols: { base: 3, xs: 4, sm: 5, md: 6, lg: 8 }, iconSize: 48, thumbSize: 200 },
}

function GridThumbnail({ node, gridSize }: { node: DriveNode; gridSize: GridSize }) {
  const [imgError, setImgError] = useState(false)
  const { iconSize, thumbSize } = gridLayout[gridSize]

  if (node.is_folder) {
    return <FileTypeIcon node={node} size={iconSize} />
  }

  if (isImageFilename(node.name) && !imgError) {
    return (
      <Image
        src={driveApi.thumbnailUrl(node.id, thumbSize)}
        fit="cover"
        w="100%"
        h="100%"
        onError={() => setImgError(true)}
      />
    )
  }

  return <FileTypeIcon node={node} size={iconSize} />
}

interface DriveGridProps {
  nodes: DriveNode[]
  selectedIds: Set<string>
  size: GridSize
  onRowClick: (e: React.MouseEvent, node: DriveNode) => void
  onRowContextMenu: (e: React.MouseEvent, node: DriveNode) => void
  onRowDoubleClick: (e: React.MouseEvent, node: DriveNode) => void
}

export function DriveGrid({
  nodes,
  selectedIds,
  size,
  onRowClick,
  onRowContextMenu,
  onRowDoubleClick,
}: DriveGridProps) {
  const { cols } = gridLayout[size]

  return (
    <SimpleGrid cols={cols}>
      {nodes.map((node) => (
        <Paper
          key={node.id}
          withBorder
          p={size === 'small' ? 6 : 'xs'}
          style={{
            cursor: 'pointer',
            backgroundColor: selectedIds.has(node.id)
              ? 'var(--mantine-color-blue-0)'
              : undefined,
          }}
          onClick={(e) => onRowClick(e, node)}
          onDoubleClick={(e) => onRowDoubleClick(e, node)}
          onContextMenu={(e) => onRowContextMenu(e, node)}
        >
          <Box
            style={{
              aspectRatio: '1',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              overflow: 'hidden',
            }}
          >
            <GridThumbnail node={node} gridSize={size} />
          </Box>
          <Text truncate size="xs" ta="center" mt={size === 'small' ? 2 : 4} lh={1.3}>
            {node.name}
          </Text>
        </Paper>
      ))}
    </SimpleGrid>
  )
}
