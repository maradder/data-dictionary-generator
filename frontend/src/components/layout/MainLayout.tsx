import { useState } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { Search, Menu } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { DocsDrawer } from './DocsDrawer'

export function MainLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const [quickSearch, setQuickSearch] = useState('')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const navigation = [
    { name: 'Dictionaries', href: '/', icon: '📚' },
    { name: 'Search', href: '/search', icon: '🔍' },
    { name: 'Upload', href: '/upload', icon: '⬆️' },
    { name: 'Database', href: '/database', icon: '🗄️' },
  ]

  const handleQuickSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (quickSearch.trim()) {
      navigate(`/search?q=${encodeURIComponent(quickSearch.trim())}`)
      setQuickSearch('')
    }
  }

  const handleMobileNavigation = (href: string) => {
    setMobileMenuOpen(false)
    navigate(href)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex h-16 items-center justify-between gap-4">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-2xl">📖</span>
            <span className="inline-block font-bold text-xl hidden sm:inline-block">
              Data Dictionary
            </span>
          </Link>

          {/* Quick Search - Hidden on mobile, shown on large screens */}
          <form onSubmit={handleQuickSearch} className="hidden lg:flex flex-1 max-w-sm">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Quick search fields..."
                value={quickSearch}
                onChange={(e) => setQuickSearch(e.target.value)}
                className="pl-9 h-9"
              />
            </div>
          </form>

          {/* Desktop Navigation - Hidden on mobile */}
          <nav className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href ||
                (item.href !== '/' && location.pathname.startsWith(item.href))

              return (
                <Link key={item.name} to={item.href}>
                  <Button
                    variant={isActive ? 'secondary' : 'ghost'}
                    className={cn(
                      'text-sm font-medium transition-colors hover:text-primary',
                      isActive ? 'text-foreground' : 'text-muted-foreground'
                    )}
                  >
                    <span className="mr-2">{item.icon}</span>
                    {item.name}
                  </Button>
                </Link>
              )
            })}
            <DocsDrawer />
          </nav>

          {/* Mobile Menu Button */}
          <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden">
                <Menu className="h-5 w-5" />
                <span className="sr-only">Toggle menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-[300px] sm:w-[400px]">
              <SheetHeader>
                <SheetTitle className="text-left">Navigation</SheetTitle>
                <SheetDescription className="text-left">
                  Access all features and pages
                </SheetDescription>
              </SheetHeader>

              <div className="mt-8 flex flex-col space-y-4">
                {/* Mobile Quick Search */}
                <form onSubmit={(e) => {
                  handleQuickSearch(e)
                  setMobileMenuOpen(false)
                }} className="mb-4">
                  <div className="relative w-full">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      type="text"
                      placeholder="Quick search fields..."
                      value={quickSearch}
                      onChange={(e) => setQuickSearch(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                </form>

                {/* Mobile Navigation Links */}
                {navigation.map((item) => {
                  const isActive = location.pathname === item.href ||
                    (item.href !== '/' && location.pathname.startsWith(item.href))

                  return (
                    <Button
                      key={item.name}
                      variant={isActive ? 'secondary' : 'ghost'}
                      className={cn(
                        'w-full justify-start text-base',
                        isActive ? 'text-foreground' : 'text-muted-foreground'
                      )}
                      onClick={() => handleMobileNavigation(item.href)}
                    >
                      <span className="mr-3 text-xl">{item.icon}</span>
                      {item.name}
                    </Button>
                  )
                })}

                {/* Help Button in Mobile Menu */}
                <div className="pt-4 border-t">
                  <DocsDrawer />
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 sm:py-8 lg:py-10">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t py-6 md:py-0">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row h-auto md:h-14 gap-2 md:gap-0 items-center justify-between">
          <p className="text-xs sm:text-sm text-muted-foreground text-center md:text-left">
            Built with FastAPI, React, and TailwindCSS
          </p>
          <p className="text-xs sm:text-sm text-muted-foreground text-center md:text-right">
            Data Dictionary Generator v1.0
          </p>
        </div>
      </footer>
    </div>
  )
}
