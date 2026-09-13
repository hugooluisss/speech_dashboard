MESSAGES = {
    'quota_exhausted': {'en': 'Quota exhausted', 'es': 'Cuota agotada'},
    'not_authenticated': {'en': 'Not authenticated', 'es': 'No estás autenticado'},
    'unknown_plan': {'en': 'Unknown or free plan', 'es': 'Plan desconocido o gratuito'},
    'no_stripe_customer': {'en': 'No Stripe customer record', 'es': 'No existe un registro de cliente de Stripe'},
    'plan_not_found': {'en': 'Plan not found', 'es': 'Plan no encontrado'},
    'admin_role_required': {'en': 'Admin role required', 'es': 'Se requiere el rol de administrador'},
}


def message(key: str, accept_language: str | None = None) -> str:
    if not isinstance(accept_language, str):
        accept_language = None
    locale = 'es' if (accept_language or '').lower().split(',')[0].strip().startswith('es') else 'en'
    return MESSAGES[key][locale]
