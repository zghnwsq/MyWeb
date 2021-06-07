from django.views import generic
from Utils.Personal import get_personal


class ListViewWithMenu(generic.ListView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context['menus'] = self.request.session.get('menus', [])
        if hasattr(self, 'parent_menu'):
            context['expand'] = getattr(self, 'parent_menu')
        # context['expand'] = PARENT_MENU
        return context
