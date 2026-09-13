import { assertKeyParity } from './index';

export const dashboard = {
  en: {
    logout: 'Log out', dashboard: 'Dashboard', yourDashboard: 'Your dashboard', currentPeriod: 'Current period', wordsUsed: 'words used', remaining: 'remaining', unlimited: 'Unlimited',
    localNoLimit: "Local transcription has no word limit. Your plan doesn't include cloud quota.", billing: 'Billing', currentPlan: 'Current plan:', choosePlan: 'Choose a plan', upgrade: 'Upgrade', manageBilling: 'Manage billing', adminDashboard: 'Admin dashboard',
    paymentHistory: 'Payment history', paymentDate: 'Date', paymentAmount: 'Amount', paymentStatus: 'Status', noPayments: 'No payments yet.', paymentHistoryError: 'Payment history is temporarily unavailable.',
    operations: 'Operations', users: 'Users', identifier: 'Identifier', plan: 'Plan', usage: 'Usage', words: 'words', language: 'Language',
  },
  es: {
    logout: 'Cerrar sesión', dashboard: 'Panel', yourDashboard: 'Tu panel', currentPeriod: 'Periodo actual', wordsUsed: 'palabras usadas', remaining: 'restantes', unlimited: 'Ilimitado',
    localNoLimit: 'La transcripción local no tiene límite de palabras. Tu plan no incluye cuota en la nube.', billing: 'Facturación', currentPlan: 'Plan actual:', choosePlan: 'Elige un plan', upgrade: 'Mejorar plan', manageBilling: 'Gestionar facturación', adminDashboard: 'Panel de administración',
    paymentHistory: 'Historial de pagos', paymentDate: 'Fecha', paymentAmount: 'Monto', paymentStatus: 'Estado', noPayments: 'Todavía no hay pagos.', paymentHistoryError: 'El historial de pagos no está disponible temporalmente.',
    operations: 'Operaciones', users: 'Usuarios', identifier: 'Identificador', plan: 'Plan', usage: 'Uso', words: 'palabras', language: 'Idioma',
  },
} as const;

assertKeyParity('dashboard', dashboard);
