import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { queryClient } from './lib/queryClient'
import { MainLayout } from './components/layout/MainLayout'
import { DictionariesListPage } from './pages/dictionaries/DictionariesListPage'
import { DictionaryUploadPage } from './pages/dictionaries/DictionaryUploadPage'
import { DictionaryDetailPage } from './pages/dictionaries/DictionaryDetailPage'
import { GlobalSearchPage } from './pages/search/GlobalSearchPage'
import { ErrorBoundary } from './components/common/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route
                index
                element={
                  <ErrorBoundary>
                    <DictionariesListPage />
                  </ErrorBoundary>
                }
              />
              <Route
                path="upload"
                element={
                  <ErrorBoundary>
                    <DictionaryUploadPage />
                  </ErrorBoundary>
                }
              />
              <Route
                path="dictionaries/:id"
                element={
                  <ErrorBoundary>
                    <DictionaryDetailPage />
                  </ErrorBoundary>
                }
              />
              <Route
                path="search"
                element={
                  <ErrorBoundary>
                    <GlobalSearchPage />
                  </ErrorBoundary>
                }
              />
            </Route>
          </Routes>
        </BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'hsl(var(--background))',
              color: 'hsl(var(--foreground))',
              border: '1px solid hsl(var(--border))',
            },
          }}
        />
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
