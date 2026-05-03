import { createBrowserRouter, Navigate } from 'react-router-dom';
import RootLayout from '../components/layout/RootLayout';
import Layout from '../components/layout/Layout';
import ProtectedRoute from '../components/auth/ProtectedRoute';
import ChatPage from '../pages/ChatPage';
// @ts-ignore
import { LoginPage, RegisterPage } from 'auth-pages';
import SetupWizard from '../pages/SetupWizard';

import KnowledgeBase from '../pages/KnowledgeBase';
import KnowledgeBaseDetail from '../pages/KnowledgeBaseDetail';
import WebsiteKnowledgeBaseDetail from '../pages/WebsiteKnowledgeBaseDetail';
import QAKnowledgeBaseDetail from '../pages/QAKnowledgeBaseDetail';
import SettingsLayout from '../pages/SettingsLayout';

import GeneralSettings from '../components/settings/GeneralSettings';
import ProfileSettings from '../components/settings/ProfileSettings';
import NotificationSettings from '../components/settings/NotificationSettings';
import ModelProvidersSettings from '../components/settings/ModelProvidersSettings';
import AboutSettings from '../components/settings/AboutSettings';

// Import SaaS routes if they exist (will be resolved via Vite alias or empty default)
// @ts-ignore
import { saasRoutes, saasPublicRoutes } from 'saas-routes';

/**
 * Router configuration for the MTN AI Chatbot application
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      // Setup wizard route (outside of Layout and ProtectedRoute)
      {
        path: 'setup',
        element: <SetupWizard />
      },
      // Authentication routes (outside of Layout)
      {
        path: 'login',
        element: <LoginPage />
      },
      {
        path: 'register',
        element: <RegisterPage />
      },
      // SaaS public routes (verify-email, etc.)
      ...(saasPublicRoutes || []),
      // Main application routes
      {
        path: '/',
        element: (
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        ),
        children: [
          {
            index: true,
            element: <Navigate to="/chat" replace />
          },
          {
            path: 'settings',
            element: <SettingsLayout />,
            children: [
              { index: true, element: <Navigate to="/settings/profile" replace /> },
              { path: 'profile', element: <ProfileSettings /> },
              { path: 'general', element: <GeneralSettings /> },
              { path: 'notifications', element: <NotificationSettings /> },
              { path: 'providers', element: <ModelProvidersSettings /> },
              { path: 'about', element: <AboutSettings /> },
              // Inject SaaS settings routes
              ...(saasRoutes || [])
                .filter((r: any) => r.path.startsWith('/settings/'))
                .map((r: any) => ({
                  ...r,
                  path: r.path.replace('/settings/', '')
                }))
            ]
          },
          {
            path: 'chat',
            element: <ChatPage />,
            children: [
              { index: true, element: null },
              { path: ':channelType/:channelId', element: null }
            ]
          },
          {
            path: 'knowledge',
            element: <KnowledgeBase/>
          },
          {
            path: 'knowledge/:id',
            element: <KnowledgeBaseDetail/>
          },
          {
            path: 'knowledge/website/:id',
            element: <WebsiteKnowledgeBaseDetail/>
          },
          {
            path: 'knowledge/qa/:id',
            element: <QAKnowledgeBaseDetail/>
          },
          {
            path: 'mtn-chat',
            element: <MtnChatPage />
          }
        ]
      }
    ]
  }
]);

// Import and export MtnChatPage
import MtnChatPage from '../pages/MtnChatPage';
export { MtnChatPage };
