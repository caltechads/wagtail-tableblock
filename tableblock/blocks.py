import json
from django import forms
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.functional import cached_property
from wagtail.core import blocks

try:
    # Imports the register_feature decorator from the 'features' module.
    from features.registry import register_feature, registry
except ImportError:
    # If features isn't installed, @register_feature becomes a noop, and the registry is empty.
    # noinspection PyUnusedLocal
    def register_feature(**kwargs):
        return lambda klass: klass
    registry = {'default': set(), 'special': set()}


DEFAULT_TABLE_OPTIONS = {
    'minSpareRows': 0,
    'startRows': 3,
    'startCols': 3,
    'colHeaders': False,
    'rowHeaders': False,
    'contextMenu': [
        'row_above',
        'row_below',
        '---------',
        'col_left',
        'col_right',
        '---------',
        'remove_row',
        'remove_col',
        '---------',
        'undo',
        'redo'
    ],
    'editor': 'text',
    'stretchH': 'all',
    'height': 108,
    'renderer': 'text',
    'autoColumnSize': False,
}


class TableInput(forms.HiddenInput):
    template_name = 'tableblock/widgets/TableWidget.html'

    def __init__(self, table_options=None, attrs=None):
        self.table_options = table_options
        super().__init__(attrs=attrs)

    def get_context(self, name, value, attrs=None):
        context = super().get_context(name, value, attrs)
        context['widget']['table_options_json'] = json.dumps(self.table_options)
        return context


class TableInputBlock(blocks.FieldBlock):

    def __init__(self, required=True, help_text=None, table_options=None, **kwargs):
        """
        CharField's 'label' and 'initial' parameters are not exposed, as Block
        handles that functionality natively (via 'label' and 'default')

        CharField's 'max_length' and 'min_length' parameters are not exposed as table
        data needs to have arbitrary length
        """
        self.table_options = self.get_table_options(table_options=table_options)
        self.field_options = {'required': required, 'help_text': help_text}
        super().__init__(**kwargs)

    @cached_property
    def field(self):
        return forms.CharField(widget=TableInput(table_options=self.table_options), **self.field_options)

    def value_from_form(self, value):
        return json.loads(value)

    def value_for_form(self, value):
        return json.dumps(value)

    def is_html_renderer(self):
        return self.table_options['renderer'] == 'html'

    def get_searchable_content(self, value):
        content = []
        for row in value.get('data', []):
            content.extend([v for v in row if v])
        return content

    def render(self, value, context=None):
        template = getattr(self.meta, 'template', None)
        if template and value:
            table_header = value['data'][0] if value.get('data', None) and len(value['data']) > 0 and value.get('first_row_is_table_header', False) else None
            first_col_is_header = value.get('first_col_is_header', False)

            if context is None:
                new_context = {}
            else:
                new_context = dict(context)

            new_context.update({
                'self': value,
                self.TEMPLATE_VAR: value,
                'table_header': table_header,
                'first_col_is_header': first_col_is_header,
                'html_renderer': self.is_html_renderer(),
                'data': value['data'][1:] if table_header else value.get('data', [])
            })
            return render_to_string(template, new_context)
        else:
            return self.render_basic(value, context=context)

    @property
    def media(self):
        # We override TableBlock's default media because its form javascript is badly written.
        return forms.Media(
            css={
                'all': [
                    'tableblock/css/handsontable-7.0.3/handsontable.full.min.css',
                    'tableblock/css/TableWidget.css'
                ]
            },
            js=[
                'tableblock/js/handsontable-7.0.3/handsontable.full.min.js',
                'tableblock/js/TableWidget.js'
            ]
        )

    def get_table_options(self, table_options=None):
        """
        Return a dict of table options using the defaults unless custom options provided

        table_options can contain any valid handsontable options:
        http://docs.handsontable.com/0.18.0/Options.html
        contextMenu: if value from table_options is True, still use default
        language: if value is not in table_options, attempt to get from envrionment
        """

        collected_table_options = DEFAULT_TABLE_OPTIONS.copy()

        if table_options is not None:
            if table_options.get('contextMenu', None) is True:
                # explicity check for True, as value could also be array
                # delete to ensure the above default is kept for contextMenu
                del table_options['contextMenu']
            collected_table_options.update(table_options)

        if 'language' not in collected_table_options:
            # attempt to gather the current set language of not provided
            language = translation.get_language()
            if language is not None and len(language) > 2:
                language = language[:2]
            collected_table_options['language'] = language

        return collected_table_options


@register_feature(feature_type='default')
class TableBlock(blocks.StructBlock):

    enable_search = blocks.BooleanBlock(
        default=False,
        help_text="Allow users to search the table's contents."
    )
    enable_pagination = blocks.BooleanBlock(
        default=False,
        help_text="If the table is very long, you may wish to paginate it, which users can navigate without leaving "
                  "the page tha the table is on."
    )
    enable_sorting = blocks.BooleanBlock(
        default=False,
        help_text="Allow users to sort the table by individual columns."
    )
    table_json = TableInputBlock(
        verbose_name='Table',
        help_text="This widget behaves very similarly to Excel. Try right-clicking to access the context menu."
    )

    class Meta:
        label = 'Table Block'
        default = None
        template = 'tableblock/blocks/TableBlock.html'
        icon = 'table'
