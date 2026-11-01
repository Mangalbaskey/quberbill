"""bharat_business/config/docs.py — App documentation metadata."""


def get_context(context):
    context.update(
        {
            "show_sidebar": True,
            "show_child_table_in_print": True,
            "no_breadcrumbs": True,
        }
    )
