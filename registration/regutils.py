# All static variables should be declared and initialized in this file.
# Since each conference from year to year will have different prices, dates, etc -- make sure you
# go in here and change the variables accordingly

import datetime


# Open 12-14-2017 @ 1800/6:00p CENTRAL (timezone is set in settings.py)
# Close 1-2-2018 @ 11:59:59
early_reg_open_date = datetime.datetime(2017, 12, 14, 18, 0, 0)
early_reg_close_date = datetime.datetime(2018, 1, 2, 23, 59, 59)
early_reg_price = '75.00'
early_reg_cap = 80  # Not official

# Open 1-3-2018 @ 12:00a CENTRAL
# Close 1-14-2018 @ 6:00p
regular_reg_open_date = datetime.datetime(2018, 1, 3, 0, 0, 0)
regular_reg_close_date = datetime.datetime(2018, 1, 14, 18, 0, 0)
regular_reg_price = '85.00'
regular_reg_cap = 280  # Not official

# Open 12-14-2017 @ 6:00p CENTRAL
# Close 1-14-2018 @ 6:00p
alumni_reg_open_date = datetime.datetime(2017, 12, 14, 18, 0, 0)
alumni_reg_close_date = datetime.datetime(2018, 1, 14, 18, 0, 0)
alumni_reg_price = '75.00'
alumni_reg_cap = 30  # Not official


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

# Member school names
member_school_names = [
    # ILLINOIS
    'Loyola University Chicago',
    'Northwestern University',
    'University of Illinois at Chicago',
    'University of Illinois at Urbana-Champaign',
    # INDIANA
    'Indiana University',
    'Indiana University Purdue University of Fort Wayne',
    'Purdue University',
    'University of Notre Dame',
    # IOWA
    'Iowa State University',
    'University of Iowa',
    # KANSAS
    'University of Kansas',
    # KENTUCKY
    'University of Louisville',
    # MICHIGAN
    'Michigan State University',
    'University of Michigan',
    'Wayne State University',
    # MINNESOTA
    'University of Minnesota',
    'St. Olaf College',
    # MISSOURI
    'St. Louis University',
    # OHIO
    'Case Western Reserve University',
    'Cleveland State University',
    'Miami University',
    'The Ohio State University',
    'University of Akron',
    'University of Cincinnati',
    'University of Toledo',
    # WISCONSIN
    'University of Wisconsin - Lacrosse',
    'University of Wisconsin - Madison',
    'University of Wisconsin - Milwaukee',
    'University of Testing - ayy lmao',
]


class MemberSchoolPresident(object):
    def __init__(self, name, email, school):
        self.name = name
        self.email = email
        self.school = school


# Need to update this list every year, unfortunately :(
member_school_presidents = []
member_school_presidents.append(MemberSchoolPresident('Eric Tran', 'etran9@uic.edu', 'University of Illinois at Chicago'))
member_school_presidents.append(MemberSchoolPresident('Tyler Tran', 'ttran82@illinois.edu', 'University of Illinois at Urbana-Champaign'))
member_school_presidents.append(MemberSchoolPresident('Thuy (Chloe) Nguyen', 'nguytb01@students.ipfw.edu', 'Indiana University Purdue University of Fort Wayne'))
member_school_presidents.append(MemberSchoolPresident('Alyssa Ngo', 'ango@nd.edu', 'University of Notre Dame'))
member_school_presidents.append(MemberSchoolPresident('Andrew Tran', 'andtran@umail.iu.edu', 'Indiana University'))
member_school_presidents.append(MemberSchoolPresident('Marilyn Lo', 'marilyn-lo@uiowa.edu', 'University of Iowa'))
member_school_presidents.append(MemberSchoolPresident('John Nguyen', 'jsnguyen@iastate.edu', 'Iowa State University'))
member_school_presidents.append(MemberSchoolPresident('Minh Thi Nguyen', 'minhthinguyen@ku.edu', 'University of Kansas'))
member_school_presidents.append(MemberSchoolPresident('Jimy Nguyen', 'j0nguy01@louisville.edu', 'University of Louisville'))
member_school_presidents.append(MemberSchoolPresident('Jessica Tran', 'tranjess@msu.edu', 'Michigan State University'))
member_school_presidents.append(MemberSchoolPresident('Jessica Jiang', 'jyjiang@umich.edu', 'University of Michigan'))
member_school_presidents.append(MemberSchoolPresident('Pele Le', 'lexxx500@umn.edu', 'University of Minnesota'))
member_school_presidents.append(MemberSchoolPresident('Sunny Vuong', 'vuong1@stolaf.edu', 'St. Olaf College'))
member_school_presidents.append(MemberSchoolPresident('Huyen Truong', 'truong.92@osu.edu', 'The Ohio State University'))
member_school_presidents.append(MemberSchoolPresident('Vy Mai', 'maivt@mail.uc.edu', 'University of Cincinnati'))
member_school_presidents.append(MemberSchoolPresident('Tuan Pham', 'tuan.pham@rockets.utoledo.edu', 'University of Toledo'))
member_school_presidents.append(MemberSchoolPresident('Kris Huynh', 'huynhtt@miamioh.edu', 'Miami University'))
member_school_presidents.append(MemberSchoolPresident('Vy Lam', 'v.h.lam@vikes.csuohio.edu', 'Cleveland State University'))
member_school_presidents.append(MemberSchoolPresident('Michael Nguyen', 'Mtn25@case.edu', 'Case Western Reserve University'))
member_school_presidents.append(MemberSchoolPresident('Karie Le', 'kle5@wisc.edu', 'University of Wisconsin - Madison'))
member_school_presidents.append(MemberSchoolPresident('Henry Tran', 'tranht@uwm.edu', 'University of Wisconsin - Milwaukee'))
member_school_presidents.append(MemberSchoolPresident('Testy Tester', 'tomng2012@gmail.com', 'University of Testing - ayy lmao'))