# -*- coding: utf-8 -*-
{
    'name': "Todo App",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
        Manages todo and task
    """,

    'author': "Amnil Internship",
    'website': "https://www.amnilintern.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        'security/ir_rules.xml',
        'security/ir.model.access.csv',

        'data/todo_stage_data.xml',
        'data/ir_cron_data.xml',

        'wizard/task_mark_complete_wizard.xml',

        'views/views.xml',
        'views/templates.xml',
        'views/todo.xml',
        'views/todo_category.xml',
        'views/todo_tag.xml',
        'views/todo_stage.xml',
        'views/res_config_settings.xml',
        'views/todo_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'images':['static/description/icon.png',] ,
}

