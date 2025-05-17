# Contrôle des rôles et permissions
ROLE_PERMISSIONS = {
    "admin": {"delete_user", "view_profile", "edit_settings", "manage_roles"},
    "user": {"view_profile"},
    "readonly": set(),
}

def has_permission(user, action):
    """
    Vérifie si l'utilisateur a le droit de faire 'action' selon son rôle.
    """
    role = user.get("role", "user")
    allowed = ROLE_PERMISSIONS.get(role, set())
    return action in allowed
