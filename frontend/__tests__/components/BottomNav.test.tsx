import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import BottomNav from '@/components/layout/BottomNav'

// next/link のモック
vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: { children: React.ReactNode; href: string }) => (
    <a href={href} {...props}>{children}</a>
  ),
}))

describe('BottomNav', () => {
  it('モバイルナビゲーションリンクが表示される', () => {
    render(<BottomNav />)

    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Talk')).toBeInTheDocument()
    expect(screen.getByText('Listen')).toBeInTheDocument()
    expect(screen.getByText('Speak')).toBeInTheDocument()
    expect(screen.getByText('Review')).toBeInTheDocument()
  })

  it('アクティブなタブがハイライトされる', () => {
    // usePathname は vitest.setup.ts で '/' を返す
    render(<BottomNav />)

    // Home リンク（href="/"）がアクティブクラスを持つ
    const homeLink = screen.getByText('Home').closest('a')
    expect(homeLink).toHaveClass('text-primary')
  })

  it('各リンクのhrefが正しい', () => {
    render(<BottomNav />)

    expect(screen.getByText('Home').closest('a')).toHaveAttribute('href', '/')
    expect(screen.getByText('Talk').closest('a')).toHaveAttribute('href', '/talk')
    expect(screen.getByText('Listen').closest('a')).toHaveAttribute('href', '/listening')
    expect(screen.getByText('Speak').closest('a')).toHaveAttribute('href', '/speaking')
    expect(screen.getByText('Review').closest('a')).toHaveAttribute('href', '/review')
  })

  it('5つのナビゲーションアイテムがある', () => {
    render(<BottomNav />)

    const links = screen.getAllByRole('link')
    expect(links).toHaveLength(5)
  })
})
