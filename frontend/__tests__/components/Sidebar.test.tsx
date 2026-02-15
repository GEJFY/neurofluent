import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import Sidebar from '@/components/layout/Sidebar'

// auth-store のモック
const mockLogout = vi.fn()
vi.mock('@/lib/stores/auth-store', () => ({
  useAuthStore: (selector: (s: Record<string, unknown>) => unknown) =>
    selector({ logout: mockLogout }),
}))

// next/link のモック
vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: { children: React.ReactNode; href: string }) => (
    <a href={href} {...props}>{children}</a>
  ),
}))

describe('Sidebar', () => {
  it('ナビゲーションリンクが表示される', () => {
    render(<Sidebar />)

    // 主要なナビゲーションラベルが表示されていることを確認
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Talk')).toBeInTheDocument()
    expect(screen.getByText('Listening')).toBeInTheDocument()
    expect(screen.getByText('Speaking')).toBeInTheDocument()
    expect(screen.getByText('Review')).toBeInTheDocument()
    expect(screen.getByText('Analytics')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('日本語ラベルが表示される', () => {
    render(<Sidebar />)

    expect(screen.getByText('ダッシュボード')).toBeInTheDocument()
    expect(screen.getByText('AIトーク')).toBeInTheDocument()
    expect(screen.getByText('リスニング')).toBeInTheDocument()
    expect(screen.getByText('スピーキング')).toBeInTheDocument()
    expect(screen.getByText('復習')).toBeInTheDocument()
    expect(screen.getByText('分析')).toBeInTheDocument()
    expect(screen.getByText('設定')).toBeInTheDocument()
  })

  it('アクティブなリンクがハイライトされる', () => {
    // usePathname は vitest.setup.ts で '/' を返すようモックされている
    render(<Sidebar />)

    // Dashboard リンク（href="/"）がアクティブクラスを持つ
    const dashboardLink = screen.getByText('Dashboard').closest('a')
    expect(dashboardLink).toHaveClass('bg-primary/10')
    expect(dashboardLink).toHaveClass('text-primary')
  })

  it('FluentEdgeロゴが表示される', () => {
    render(<Sidebar />)

    expect(screen.getByText('FluentEdge')).toBeInTheDocument()
    expect(screen.getByText('AI English Training')).toBeInTheDocument()
  })

  it('テーマ切り替えボタンが動作する', async () => {
    const user = userEvent.setup()
    render(<Sidebar />)

    // 初期状態はダークモード（ライトモード切り替えボタンが表示）
    const themeButton = screen.getByText('ライトモード')
    expect(themeButton).toBeInTheDocument()

    // クリックしてトグル
    await user.click(themeButton)
    expect(screen.getByText('ダークモード')).toBeInTheDocument()
  })

  it('ログアウトボタンがクリックされるとlogoutが呼ばれる', async () => {
    const user = userEvent.setup()
    render(<Sidebar />)

    const logoutButton = screen.getByText('ログアウト')
    await user.click(logoutButton)

    expect(mockLogout).toHaveBeenCalled()
  })
})
