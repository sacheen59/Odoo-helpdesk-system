# -*- coding: utf-8 -*-
{
    'name': "HelpDesk App",

    'summary': "Manage your helpdesk tickets",

    'description': """
        Long description of module's purpose
    """,

    'author': "Amnil Internship",
    'website': "https://www.amnilintern.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website','mail'],

    # always
    'data': [
        'security/ir_rules.xml',
        'security/ir.model.access.csv',

        'report/ir_action_report_templates.xml',
        'report/ir_actions_report.xml',

        'data/helpdesk_ticket_stage.xml',

        'wizard/ticket_stage_remark_wizard.xml',
        'wizard/helpdesk_report_open_wizard.xml',


        'views/helpdesk_portal_templates.xml',
        'views/helpdesk_portal_received_form_templates.xml',

        'views/views.xml',
        'views/templates.xml',
        'views/helpdesk_tickets.xml',
        'views/helpdesk_tickets_category.xml',
        'views/helpdesk_tickets_tag.xml',
        'views/helpdesk_team.xml',
        'views/helpdesk_ticket_stage.xml',
        'views/helpdesk_menu.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

