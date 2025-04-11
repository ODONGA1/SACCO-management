from django.urls import path
from core import views, transfer, transaction, payment_request, credit_card


app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    
    # Transfers
    path("search-account/", transfer.search_users_account_number, name="search-account"),
    path("amount-transfer/<account_number>/", transfer.AmountTransfer, name="amount-transfer"),
    path("amount-transfer-process/<account_number>/", transfer.AmountTransferProcess, name="amount-transfer-process"),
    path("transfer-confirmation/<account_number>/<transaction_id>/", transfer.TransferConfirmation, name="transfer-confirmation"),
    path("transfer-process/<account_number>/<transaction_id>/", transfer.TransferProcess, name="transfer-process"),
    path("transfer-completed/<account_number>/<transaction_id>/", transfer.TransferCompleted, name="transfer-completed"),


    # transactions
    path("transactions/", transaction.transaction_lists, name="transactions"),
    path("transaction-detail/<transaction_id>/", transaction.transaction_detail, name="transaction-detail"),
    # path('transactions/', views.transactions, name='transactions'),
    
    # Payment Request
    path("request-search-account/", payment_request.SearchUsersRequest, name="request-search-account"),
    path("amount-request/<account_number>/", payment_request.AmountRequest, name="amount-request"),
    path("amount-request-process/<account_number>/", payment_request.AmountRequestProcess, name="amount-request-process"),
    path("amount-request-confirmation/<account_number>/<transaction_id>/", payment_request.AmountRequestConfirmation, name="amount-request-confirmation"),
    path("amount-request-final-process/<account_number>/<transaction_id>/", payment_request.AmountRequestFinalProcess, name="amount-request-final-process"),
    path("amount-request-completed/<account_number>/<transaction_id>/", payment_request.RequestCompleted, name="amount-request-completed"),


    # Request Settlement
    path("settlement-confirmation/<account_number>/<transaction_id>/", payment_request.settlement_confirmation, name="settlement-confirmation"),
    path("settlement-processing/<account_number>/<transaction_id>/", payment_request.settlement_processing, name="settlement-processing"),
    path("settlement-completed/<account_number>/<transaction_id>/", payment_request.SettlementCompleted, name="settlement-completed"),
    path("delete-request/<account_number>/<transaction_id>/", payment_request.deletepaymentrequest, name="delete-request"),



    # Credit Card URLS
    path("card/<card_id>/", credit_card.card_detail, name="card-detail"),
    path("fund-credit-card/<card_id>/", credit_card.fund_credit_card, name="fund-credit-card"),
    path("withdraw_fund/<card_id>/", credit_card.withdraw_fund, name="withdraw_fund"),
    path("delete_card/<card_id>/", credit_card.delete_card, name="delete_card"),
    
    # zeta
    
    # dashboard paths

    path('', views.indexPage,name='indexPage'),
    path('dashboard_default', views.dashboard_default,name='dashboard_default'),
    path('dashboard_ecommerce', views.dashboard_ecommerce,name='dashboard_ecommerce'),
    path('dashboard_crypto', views.dashboard_crypto,name='dashboard_crypto'),


    # widgets paths 

    path('widgets_general', views.widgets_general,name='widgets_general'),
    path('widgets_chart', views.widgets_chart,name='widgets_chart'),

    # page layout paths

    path('page_layout_boxed',views.page_layout_boxed,name='page_layout_boxed'),
    path('page_layout_rtl',views.page_layout_rtl,name='page_layout_rtl'),
    path('page_layout_dark',views.page_layout_dark,name='page_layout_dark'),
    path('page_layout_hide_nav_scroll',views.page_layout_hide_nav_scroll,name='page_layout_hide_nav_scroll'),
    path('page_layout_footer_light',views.page_layout_footer_light,name='page_layout_footer_light'),
    path('page_layout_footer_dark',views.page_layout_footer_dark,name='page_layout_footer_dark'),
    path('page_layout_footer_fixed',views.page_layout_footer_fixed,name='page_layout_footer_fixed'),

    # project paths

    path('project_project_list',views.project_project_list,name='project_project_list'),
    path('project_create_new',views.project_create_new,name='project_create_new'),

    # file manager path

    path('file_manager',views.file_manager,name='file_manager'),

    # kanban board path

    path('kanban_board',views.kanban_board,name='kanban_board'),

    # Ecommerce paths

    path('ecommerce_product_view',views.ecommerce_product_view,name='ecommerce_product_view'),
    path('ecommerce_product_page',views.ecommerce_product_page,name='ecommerce_product_page'),
    path('ecommerce_product_list',views.ecommerce_product_list,name='ecommerce_product_list'),
    path('ecommerce_payment_details',views.ecommerce_payment_details,name='ecommerce_payment_details'),
    path('ecommerce_order_history',views.ecommerce_order_history,name='ecommerce_order_history'),
    path('ecommerce_invoice',views.ecommerce_invoice,name='ecommerce_invoice'),
    path('ecommerce_cart',views.ecommerce_cart,name='ecommerce_cart'),
    path('ecommerce_wishlist',views.ecommerce_wishlist,name='ecommerce_wishlist'),
    path('ecommerce_checkout',views.ecommerce_checkout,name='ecommerce_checkout'),
    path('ecommerce_pricing',views.ecommerce_pricing,name='ecommerce_pricing'),

    # email paths

    path('email_email_app',views.email_email_app,name='email_email_app'),
    path('email_read_mail',views.email_read_mail,name='email_read_mail'),
    path('email_email_compose',views.email_email_compose,name='email_email_compose'),
    
    # chat paths

    path('chat_chat_app',views.chat_chat_app,name='chat_chat_app'),
    path('chat_video_chat',views.chat_video_chat,name='chat_video_chat'),

    # users paths

    path('users_users_profile',views.users_users_profile,name='users_users_profile'),
    path('users_users_edit',views.users_users_edit,name='users_users_edit'),
    path('users_users_card',views.users_users_card,name='users_users_card'),

    # bookmarks path

    path('bookmarks',views.bookmarks,name='bookmarks'),

    # contacts path

    path('contacts',views.contacts,name='contacts'),

    # tasks paths

    path('tasks',views.tasks,name='tasks'),

    # calendar path

    path('calendar',views.calendar,name='calendar'),

    # social app path

    path('social_app',views.social_app,name='social_app'),

    # to do path

    path('to_do_view',views.to_do_view,name='to_do_view'),
    path('to_do_database',views.to_do_database,name='to_do_database'),
    path('delete/<str:pk>/', views.deleteTask, name="delete"),
    path('updateTask/<str:pk>/', views.updateTask,name='updateTask'),
    path('markAllComplete/', views.markAllComplete, name='markAllComplete'),
    path('markAllIncomplete/', views.markAllIncomplete, name='markAllIncomplete'),
    # search website path

    path('search_website',views.search_website,name='search_website'),

    # form path

    path('form_form_validation',views.form_form_validation,name='form_form_validation'),
    path('form_base_inputs',views.form_base_inputs,name='form_base_inputs'),
    path('checkbox_and_radio',views.checkbox_and_radio,name='checkbox_and_radio'),
    path('input_groups',views.input_groups,name='input_groups'),
    path('mega_options',views.mega_options,name='mega_options'),
    path('datepicker',views.datepicker,name='datepicker'),
    path('timepicker',views.timepicker,name='timepicker'),
    path('datetimepicker',views.datetimepicker,name='datetimepicker'),
    path('daterangepicker',views.daterangepicker,name='daterangepicker'),
    path('touchspin',views.touchspin,name='touchspin'),
    path('select2',views.select2,name='select2'),
    path('switch',views.switch,name='switch'),
    path('typeahead',views.typeahead,name='typeahead'),
    path('clipboard',views.clipboard,name='clipboard'),
    path('default_form',views.default_form,name='default_form'),
    path('form_wizard_1',views.form_wizard_1,name='form_wizard_1'),
    path('form_wizard_2',views.form_wizard_2,name='form_wizard_2'),
    path('form_wizard_3',views.form_wizard_3,name='form_wizard_3'),


    # tables paths

    # bootstrap tables

    path('bootstrap_basic_tables',views.bootstrap_basic_tables,name='bootstrap_basic_tables'),
    path('bootstrap_border_tables',views.bootstrap_border_tables,name='bootstrap_border_tables'),
    path('bootstrap_sizing_tables',views.bootstrap_sizing_tables,name='bootstrap_sizing_tables'),
    path('bootstrap_styling_tables',views.bootstrap_styling_tables,name='bootstrap_styling_tables'),
    path('bootstrap_table_components',views.bootstrap_table_components,name='bootstrap_table_components'),

    # data tables

    path('data_tables_advance_init',views.data_tables_advance_init,name='data_tables_advance_init'),
    path('data_tables_AJAX',views.data_tables_AJAX,name='data_tables_AJAX'),
    path('data_tables_API',views.data_tables_API,name='data_tables_API'),
    path('data_tables_basic_init',views.data_tables_basic_init,name='data_tables_basic_init'),
    path('data_tables_data_source',views.data_tables_data_source,name='data_tables_data_source'),
    path('data_tables_plug_in',views.data_tables_plug_in,name='data_tables_plug_in'),
    path('data_tables_server_side',views.data_tables_server_side,name='data_tables_server_side'),
    path('data_tables_styling',views.data_tables_styling,name='data_tables_styling'),

    # ex data tables

    path('ex_data_tables_auto_fill',views.ex_data_tables_auto_fill,name='ex_data_tables_auto_fill'),
    path('ex_data_tables_basic_button',views.ex_data_tables_basic_button,name='ex_data_tables_basic_button'),
    path('ex_data_tables_column_reorder',views.ex_data_tables_column_reorder,name='ex_data_tables_column_reorder'),
    path('ex_data_tables_fixed_header',views.ex_data_tables_fixed_header,name='ex_data_tables_fixed_header'),
    path('ex_data_tables_html_5_export',views.ex_data_tables_html_5_export,name='ex_data_tables_html_5_export'),
    path('ex_data_tables_key_table',views.ex_data_tables_key_table,name='ex_data_tables_key_table'),
    path('ex_data_tables_responsive',views.ex_data_tables_responsive,name='ex_data_tables_responsive'),
    path('ex_data_tables_row_reorder',views.ex_data_tables_row_reorder,name='ex_data_tables_row_reorder'),
    path('ex_data_tables_scroller',views.ex_data_tables_scroller,name='ex_data_tables_scroller'),

    # js grid table

    path('js_grid_table',views.js_grid_table,name='js_grid_table'),


    # ui kits paths

    path('ui_kits_accordion',views.ui_kits_accordion,name='ui_kits_accordion'),
    path('ui_kits_alert',views.ui_kits_alert,name='ui_kits_alert'),
    path('ui_kits_avatars',views.ui_kits_avatars,name='ui_kits_avatars'),
    path('ui_kits_dropdown',views.ui_kits_dropdown,name='ui_kits_dropdown'),
    path('ui_kits_grid',views.ui_kits_grid,name='ui_kits_grid'),
    path('ui_kits_helper_classes',views.ui_kits_helper_classes,name='ui_kits_helper_classes'),
    path('ui_kits_list',views.ui_kits_list,name='ui_kits_list'),
    path('ui_kits_loader',views.ui_kits_loader,name='ui_kits_loader'),
    path('ui_kits_modal',views.ui_kits_modal,name='ui_kits_modal'),
    path('ui_kits_popover',views.ui_kits_popover,name='ui_kits_popover'),
    path('ui_kits_progress_bar',views.ui_kits_progress_bar,name='ui_kits_progress_bar'),
    path('ui_kits_state_color',views.ui_kits_state_color,name='ui_kits_state_color'),
    path('ui_kits_tag_pills',views.ui_kits_tag_pills,name='ui_kits_tag_pills'),
    path('ui_kits_toast',views.ui_kits_toast,name='ui_kits_toast'),
    path('ui_kits_tooltip',views.ui_kits_tooltip,name='ui_kits_tooltip'),
    path('ui_kits_typography',views.ui_kits_typography,name='ui_kits_typography'),

    # ui kits tabs paths

    path('ui_kits_tabs_bootstrap',views.ui_kits_tabs_bootstrap,name='ui_kits_tabs_bootstrap'),
    path('ui_kits_tabs_line',views.ui_kits_tabs_line,name='ui_kits_tabs_line'),

    # bonue ui paths

    path('bonus_ui_basic_card',views.bonus_ui_basic_card,name='bonus_ui_basic_card'),
    path('bonus_ui_bootstrap_notify',views.bonus_ui_bootstrap_notify,name='bonus_ui_bootstrap_notify'),
    path('bonus_ui_breadcrumb',views.bonus_ui_breadcrumb,name='bonus_ui_breadcrumb'),
    path('bonus_ui_creative_card',views.bonus_ui_creative_card,name='bonus_ui_creative_card'),
    path('bonus_ui_dragable_card',views.bonus_ui_dragable_card,name='bonus_ui_dragable_card'),
    path('bonus_ui_dropzone',views.bonus_ui_dropzone,name='bonus_ui_dropzone'),
    path('bonus_ui_image_cropper',views.bonus_ui_image_cropper,name='bonus_ui_image_cropper'),
    path('bonus_ui_modal_animated',views.bonus_ui_modal_animated,name='bonus_ui_modal_animated'),
    path('bonus_ui_owl_carousel',views.bonus_ui_owl_carousel,name='bonus_ui_owl_carousel'),
    path('bonus_ui_pagination',views.bonus_ui_pagination,name='bonus_ui_pagination'),
    path('bonus_ui_range_slider',views.bonus_ui_range_slider,name='bonus_ui_range_slider'),
    path('bonus_ui_rating',views.bonus_ui_rating,name='bonus_ui_rating'),
    path('bonus_ui_ribbons',views.bonus_ui_ribbons,name='bonus_ui_ribbons'),
    path('bonus_ui_scrollable',views.bonus_ui_scrollable,name='bonus_ui_scrollable'),
    path('bonus_ui_steps',views.bonus_ui_steps,name='bonus_ui_steps'),
    path('bonus_ui_sticky',views.bonus_ui_sticky,name='bonus_ui_sticky'),
    path('bonus_ui_sweet_alert2',views.bonus_ui_sweet_alert2,name='bonus_ui_sweet_alert2'),
    path('bonus_ui_tabbed_card',views.bonus_ui_tabbed_card,name='bonus_ui_tabbed_card'),
    path('bonus_ui_tour',views.bonus_ui_tour,name='bonus_ui_tour'),
    path('bonus_ui_tree',views.bonus_ui_tree,name='bonus_ui_tree'),

    # bonus ui timeline paths

    path('bonus_ui_timeline_1',views.bonus_ui_timeline_1,name='bonus_ui_timeline_1'),
    path('bonus_ui_timeline_2',views.bonus_ui_timeline_2,name='bonus_ui_timeline_2'),

    # builders paths

    path('button_builder',views.button_builder,name='button_builder'),
    path('form_builder_1',views.form_builder_1,name='form_builder_1'),
    path('form_builder_2',views.form_builder_2,name='form_builder_2'),
    path('page_builder',views.page_builder,name='page_builder'),

    # animation paths

    path('animate',views.animate,name='animate'),
    path('scroll_reveal',views.scroll_reveal,name='scroll_reveal'),
    path('AOS_animation',views.AOS_animation,name='AOS_animation'),
    path('tilt_animation',views.tilt_animation,name='tilt_animation'),
    path('wow_animation',views.wow_animation,name='wow_animation'),

    # icons paths

    path('flag_icon',views.flag_icon,name='flag_icon'),
    path('fontawesome_icon',views.fontawesome_icon,name='fontawesome_icon'),
    path('ico_icon',views.ico_icon,name='ico_icon'),
    path('thimify_icon',views.thimify_icon,name='thimify_icon'),
    path('feather_icon',views.feather_icon,name='feather_icon'),
    path('whether_icon',views.whether_icon,name='whether_icon'),

    # buttons path

    path('buttons',views.buttons,name='buttons'),

    # charts paths

    path('apex_chart',views.apex_chart,name='apex_chart'),
    path('google_chart',views.google_chart,name='google_chart'),
    path('sparkline_chart',views.sparkline_chart,name='sparkline_chart'),
    path('flot_chart',views.flot_chart,name='flot_chart'),
    path('knob_chart',views.knob_chart,name='knob_chart'),
    path('morris_chart',views.morris_chart,name='morris_chart'),
    path('chartjs',views.chartjs,name='chartjs'),
    path('chartist',views.chartist,name='chartist'),
    path('peity_chart',views.peity_chart,name='peity_chart'),



    # sample page path

    path('sample_page',views.sample_page,name='sample_page'),

    # internationalization path

    path('internationalization',views.internationalization,name='internationalization'),

    # others path
    # error pages

    path('error_page_1',views.error_page_1,name='error_page_1'),
    path('error_page_2',views.error_page_2,name='error_page_2'),
    path('error_page_3',views.error_page_3,name='error_page_3'),
    path('error_page_4',views.error_page_4,name='error_page_4'),

    # authentication paths

    path('login',views.login_simple,name='login'),
    path('login_simple',views.login_simple,name='login_simple'),
    path('login_with_bg_image',views.login_with_bg_image,name='login_with_bg_image'),
    path('login_with_image_two',views.login_with_image_two,name='login_with_image_two'),
    path('login_with_validation',views.login_with_validation,name='login_with_validation'),
    path('login_with_tooltip',views.login_with_tooltip,name='login_with_tooltip'),
    path('login_with_sweetalert',views.login_with_sweetalert,name='login_with_sweetalert'),
    path('register_simple',views.register_simple,name='register_simple'),
    path('register_with_bg_image',views.register_with_bg_image,name='register_with_bg_image'),
    path('register_with_bg_video',views.register_with_bg_video,name='register_with_bg_video'),
    path('unlock_user',views.unlock_user,name='unlock_user'),
    path('forget_password',views.forget_password,name='forget_password'),
    path('create_password',views.create_password,name='create_password'),
    path('maintenance',views.maintenance,name='maintenance'),
    path('logout_view',views.logout_view,name='logout_view'),


    # coming soon paths

    path('coming_simple',views.coming_simple,name='coming_simple'),
    path('coming_with_bg_image',views.coming_with_bg_image,name='coming_with_bg_image'),

    # email templates paths
    
    path('basic_email',views.basic_email,name='basic_email'),
    path('basic_with_header',views.basic_with_header,name='basic_with_header'),
    path('email_template_2',views.email_template_2,name='email_template_2'),
    path('ecommerce_email',views.ecommerce_email,name='ecommerce_email'),
    path('order_success',views.order_success,name='order_success'),

    path('email_application',views.email_application,name='email_application'),

    # gallery paths

    path('gallery_grid_simple',views.gallery_grid_simple,name='gallery_grid_simple'),
    path('gallery_grid_desc',views.gallery_grid_desc,name='gallery_grid_desc'),
    path('masonry_gallery',views.masonry_gallery,name='masonry_gallery'),
    path('masonry_with_desc',views.masonry_with_desc,name='masonry_with_desc'),
    path('hover_effect',views.hover_effect,name='hover_effect'),

    # blog paths

    path('blog_details',views.blog_details,name='blog_details'),
    path('blog_single',views.blog_single,name='blog_single'),
    path('add_post',views.add_post,name='add_post'),

    # faq path

    path('faq',views.faq,name='faq'),

    # job search paths

    path('cards_view',views.cards_view,name='cards_view'),
    path('list_view',views.list_view,name='list_view'),
    path('job_details',views.job_details,name='job_details'),
    path('apply',views.apply,name='apply'),

    # learning paths

    path('learning_list',views.learning_list,name='learning_list'),
    path('detailed_course',views.detailed_course,name='detailed_course'),

    # maps paths

    path('maps_js',views.maps_js,name='maps_js'),
    path('vector_maps',views.vector_maps,name='vector_maps'),

    # editor paths

    path('summer_note',views.summer_note,name='summer_note'),
    path('ck_editor',views.ck_editor,name='ck_editor'),
    path('mde_editor',views.mde_editor,name='mde_editor'),
    path('ace_code_editor',views.ace_code_editor,name='ace_code_editor'),

    # knowledgebase paths

    path('knowledgebase',views.knowledgebase,name='knowledgebase'),
    path('knowledge_category',views.knowledge_category,name='knowledge_category'),
    path('knowledge_detail',views.knowledge_detail,name='knowledge_detail'),

    # support ticket path

    path('support_ticket',views.support_ticket,name='support_ticket'),



]
