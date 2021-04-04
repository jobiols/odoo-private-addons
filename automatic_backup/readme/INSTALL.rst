To install this module, you need to:

#. Verify dependencies in dependencies.txt
#. Install the module
#. limit_time_real parameter

    When you've configured your Odoo instance to run with workers you should change the
    default value of limit_time_real (as this defaults to 120). You can configure the value
    in your odoo.conf to the appropriate number in case of a large database backup.
    This is required when max_cron_threads > 0 to avoid worker timeout during the backup.

#. review this... >> --load / server_wide_modules parameter
    In V12, V13 and V14 Odoo will need the values 'base' and 'web' set if you use the
    --load (or server_wide_modules) parameter. Without these values set you will get a
    404 NOT FOUND from the backup module. For more information see
    https://github.com/Yenthe666/auto_backup/issues/122
