from context.app_context import ApplicationContext


class ContextBuilder:

    @staticmethod
    def build_application_context(
        app,
        current_user
    ) -> ApplicationContext:

        return ApplicationContext(
            current_user=current_user,
            db_pool=app.state.db_pool
        )