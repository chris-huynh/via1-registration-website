import datetime

# 12-14-2017 @ 1800/6:00p CENTRAL (timezone is in settings.py)
early_reg_date = datetime.datetime(2017, 12, 14, 18, 0, 0)
early_reg_price = '75.00'

regular_reg_price = '85.00'

alumni_reg_price = '85.00'

# For PayPal Buttons (see views.py)
paypal_email = 'finance@uvsamidwest.org'
event_name = 'VIA-1 2017'


# For PayPal SANDBOX (use these for testing)
pp_sandbox_merchant_email = 'via1-merchant@uvsamidwest.org'


# List of email handles of all UVSA-MW member schools
member_school_emails = [
    # ILLINOIS
    'uic.edu',
    'illinois.edu',
    'luc.edu',
    'u.northwestern.edu',
    # INDIANA
    'purdue.edu',
    'students.ipfw.edu',
    'nd.edu',
    'umail.iu.edu',
    # IOWA
    'uiowa.edu',
    'iastate.edu',
    # KANSAS
    'ku.edu',
    # KENTUCKY
    'louisville.edu',
    # MICHIGAN
    'umich.edu',
    'msu.edu',
    'wayne.edu',
    # MINNESOTA
    'umn.edu',
    'stolaf.edu',
    'stcloudstate.edu',
    # MISSOURI
    'slu.edu',
    # OHIO
    'osu.edu',
    'mail.uc.edu',
    'zips.uakron.edu',
    'rockets.utoledo.edu',
    'miamioh.edu',
    'vikes.csuohio.edu',
    'case.edu',
    # WISCONSIN
    'wisc.edu',
    'uwm.edu',
    'uwlax.edu'
]


def is_member_school(school):
    if school in member_school_emails:
        return True
    else:
        return False
