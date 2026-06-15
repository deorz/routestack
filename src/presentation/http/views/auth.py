def render_admin_login_page(error_message: str | None = None) -> str:
    error_markup = f'<p role="alert">{error_message}</p>' if error_message else ""
    return (
        "<!doctype html>"
        '<html lang="en">'
        "<body>"
        f"{error_markup}"
        '<form method="post" action="/admin/login">'
        '<label>Login <input name="login" autocomplete="username"></label>'
        '<label>Password <input type="password" name="password" autocomplete="current-password"></label>'
        '<button type="submit">Sign in</button>'
        "</form>"
        "</body>"
        "</html>"
    )
