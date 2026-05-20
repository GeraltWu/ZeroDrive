/** 按扩展名判断（后端暂无 mime 字段时） */
const VIDEO_EXT = new Set(['mp4', 'webm', 'ogv', 'm4v', 'mov'])
const AUDIO_EXT = new Set(['mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac', 'opus'])
const IMAGE_EXT = new Set(['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'avif', 'ico'])

export type MediaPreviewKind = 'video' | 'audio' | 'image'

export function getMediaPreviewKind(filename: string): MediaPreviewKind | null {
  const i = filename.lastIndexOf('.')
  if (i < 0 || i === filename.length - 1) return null
  const ext = filename.slice(i + 1).toLowerCase()
  if (VIDEO_EXT.has(ext)) return 'video'
  if (AUDIO_EXT.has(ext)) return 'audio'
  if (IMAGE_EXT.has(ext)) return 'image'
  return null
}
