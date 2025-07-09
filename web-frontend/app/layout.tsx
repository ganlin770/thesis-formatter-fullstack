import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: '毕业论文格式化工具',
  description: '快速格式化毕业论文，确保符合学校规范要求',
  keywords: ['毕业论文', '格式化', '学术写作', '论文格式'],
  authors: [{ name: '论文格式化工具团队' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#3b82f6',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content={metadata.description || ''} />
        <meta name="keywords" content={metadata.keywords as string} />
        <meta name="theme-color" content="#3b82f6" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
      </head>
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          {/* 导航栏 */}
          <nav className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <h1 className="text-xl font-bold text-gray-900">
                      毕业论文格式化工具
                    </h1>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <button className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                    帮助
                  </button>
                  <button className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                    关于
                  </button>
                </div>
              </div>
            </div>
          </nav>

          {/* 主要内容 */}
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
              {children}
            </div>
          </main>

          {/* 页脚 */}
          <footer className="bg-white border-t border-gray-200 mt-auto">
            <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center">
                <div className="text-sm text-gray-500">
                  © 2024 毕业论文格式化工具. 保留所有权利.
                </div>
                <div className="flex space-x-6">
                  <a href="#" className="text-sm text-gray-500 hover:text-gray-700">
                    隐私政策
                  </a>
                  <a href="#" className="text-sm text-gray-500 hover:text-gray-700">
                    使用条款
                  </a>
                  <a href="#" className="text-sm text-gray-500 hover:text-gray-700">
                    联系我们
                  </a>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}