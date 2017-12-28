# All static variables should be declared and initialized in this file.
# Since each conference from year to year will have different prices, dates, etc -- make sure you
# go in here and change the variables accordingly

# TODO Don't forget to remove fake school below

import datetime


# TODO Currently Unused. Remove?
class AttendeeTypes:
    EARLY_REG_ATTENDEE = '1'
    REGULAR_REG_ATTENDEE = '2'
    ALUMNI_REG_ATTENDEE = '3'
    STAFF_REG_ATTENDEE = '4'


class RegisterTypes:
    EARLY_REG = 'early_registration'
    EARLY_REG_HOTEL = 'early_registration_and_hotel'
    REGULAR_REG = 'regular_registration'
    REGULAR_REG_HOTEL = 'regular_registration_and_hotel'
    ALUMNI_REG = 'alumni_registration'
    ALUMNI_REG_HOTEL = 'alumni_registration_and_hotel'
    STAFF_REG = 'staff_registration'
    STAFF_REG_HOTEL = 'staff_registration_and_hotel'


class RegisterPrices:
    EARLY_REG_PRICE = 75
    REGULAR_REG_PRICE = 85
    ALUMNI_REG_PRICE = 75
    STAFF_REG_PRICE = 75
    BANQUET_PRICE = 50     # Probably don't need -- banquet-only will probably be handled manually
    HOTEL_BUNDLE_PRICE = 60
    HOTEL_PRICE = 65   # Hotel purchased separately is an additional $5


class RegisterCaps:
    EARLY_REG_CAP = 80
    REGULAR_REG_CAP = 176
    ALUMNI_REG_CAP = 30
    STAFF_REG_CAP = 83


class HotelPaymentTypes:
    SINGLE_SPOT = 'single_spot'
    WHOLE_ROOM = 'whole_room'


# Open 12-14-2017 @ 1800/6:00p CENTRAL (timezone is set in settings.py)
# Close 1-3-2018 @ 11:59:59
early_reg_open_date = datetime.datetime(2017, 12, 14, 18, 0, 0)
early_reg_close_date = datetime.datetime(2018, 1, 3, 23, 59, 59)

# Open 1-4-2018 @ 6:00p CENTRAL
# Close 1-18-2018 @ 11:59p
regular_reg_open_date = datetime.datetime(2018, 1, 4, 18, 0, 0)
regular_reg_close_date = datetime.datetime(2018, 1, 18, 23, 59, 59)

# Open 1-4-2017 @ 6:00p CENTRAL
# Close 1-18-2018 @ 11:59p
alumni_reg_open_date = datetime.datetime(2018, 1, 4, 18, 0, 0)
alumni_reg_close_date = datetime.datetime(2018, 1, 18, 23, 59, 59)


payment_refund_deadline = datetime.datetime(2018, 2, 14, 23, 59, 59)
staff_payment_deadline = datetime.datetime(2018, 2, 7, 23, 59, 59)

roommate_deadline = datetime.datetime(2018, 3, 1, 23, 59, 59)


graduation_years = [
    2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023,
    2024, 2025]


default_pronouns = [
    'he_him_his',
    'she_her_hers',
    'they_them_theirs'
]


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
    # IU has 3 different email handles
    'umail.iu.edu',
    'iu.edu',
    'indiana.edu',
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
    # 'wayne.edu',  # Inactive
    # MINNESOTA
    'umn.edu',
    'stolaf.edu',
    # MISSOURI
    # 'slu.edu',    # Inactive
    # OHIO
    # OSU has 2 different email handles
    'buckeyemail.osu.edu',
    'osu.edu',
    'mail.uc.edu',
    # 'zips.uakron.edu',  # Inactive
    'rockets.utoledo.edu',
    'miamioh.edu',
    'vikes.csuohio.edu',
    'case.edu',
    # WISCONSIN
    'wisc.edu',
    'uwm.edu',
    # 'uwlax.edu'   # Inactive
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
    'Indiana University – Purdue University Indianapolis',
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
    #'Wayne State University',  # Inactive
    # MINNESOTA
    'University of Minnesota',
    'St. Olaf College',
    # MISSOURI
    # 'St. Louis University',   # Inactive
    # OHIO
    'Case Western Reserve University',
    'Cleveland State University',
    'Miami University',
    'The Ohio State University',
    # 'University of Akron',    # Inactive
    'University of Cincinnati',
    'University of Toledo',
    # WISCONSIN
    # 'University of Wisconsin - Lacrosse', # Inactive
    'University of Wisconsin - Madison',
    'University of Wisconsin - Milwaukee',
    #'University of Testing - ayy lmao',
]


class MemberSchoolPresident(object):
    def __init__(self, name, email, school):
        self.name = name
        self.email = email
        self.school = school


# Need to update this list every year, unfortunately :(
# Note that not every member school is in this list -- If they didn't supply UVSA-MW with contact info, then they aren't gonna be listed
member_school_presidents = []
# Illinois
member_school_presidents.append(MemberSchoolPresident('Eric Tran', 'etran9@uic.edu', 'University of Illinois at Chicago'))
member_school_presidents.append(MemberSchoolPresident('Tyler Tran', 'ttran82@illinois.edu', 'University of Illinois at Urbana-Champaign'))
# Missing Northwestern University
# Missing Loyola Unviersity Chicago
# Indiana
member_school_presidents.append(MemberSchoolPresident('Brandon Do', 'dob@purdue.edu', 'Purdue University'))
member_school_presidents.append(MemberSchoolPresident('Thuy (Chloe) Nguyen', 'nguytb01@students.ipfw.edu', 'Indiana University Purdue University of Fort Wayne'))
member_school_presidents.append(MemberSchoolPresident('Alyssa Ngo', 'ango@nd.edu', 'University of Notre Dame'))
member_school_presidents.append(MemberSchoolPresident('Andrew Tran', 'andtran@umail.iu.edu', 'Indiana University'))
member_school_presidents.append(MemberSchoolPresident('Nick Luc', 'nluc@umail.iu.edu', 'Indiana University – Purdue University Indianapolis'))
# Iowa
member_school_presidents.append(MemberSchoolPresident('Marilyn Lo', 'marilyn-lo@uiowa.edu', 'University of Iowa'))
member_school_presidents.append(MemberSchoolPresident('John Nguyen', 'jsnguyen@iastate.edu', 'Iowa State University'))
# Kansas
member_school_presidents.append(MemberSchoolPresident('Minh Thi Nguyen', 'minhthinguyen@ku.edu', 'University of Kansas'))
# Kentucky
member_school_presidents.append(MemberSchoolPresident('Jimy Nguyen', 'j0nguy01@louisville.edu', 'University of Louisville'))
# Michigan
member_school_presidents.append(MemberSchoolPresident('Jessica Tran', 'tranjess@msu.edu', 'Michigan State University'))
member_school_presidents.append(MemberSchoolPresident('Jessica Jiang', 'jyjiang@umich.edu', 'University of Michigan'))
# Minnesota
member_school_presidents.append(MemberSchoolPresident('Pele Le', 'lexxx500@umn.edu', 'University of Minnesota'))
member_school_presidents.append(MemberSchoolPresident('Sunny Vuong', 'vuong1@stolaf.edu', 'St. Olaf College'))
# Ohio
member_school_presidents.append(MemberSchoolPresident('Huyen Truong', 'truong.92@osu.edu', 'The Ohio State University'))
member_school_presidents.append(MemberSchoolPresident('Vy Mai', 'maivt@mail.uc.edu', 'University of Cincinnati'))
member_school_presidents.append(MemberSchoolPresident('Tuan Pham', 'tuan.pham@rockets.utoledo.edu', 'University of Toledo'))
member_school_presidents.append(MemberSchoolPresident('Kris Huynh', 'huynhtt@miamioh.edu', 'Miami University'))
member_school_presidents.append(MemberSchoolPresident('Vy Lam', 'v.h.lam@vikes.csuohio.edu', 'Cleveland State University'))
member_school_presidents.append(MemberSchoolPresident('Michael Nguyen', 'Mtn25@case.edu', 'Case Western Reserve University'))
# Wisconsin
member_school_presidents.append(MemberSchoolPresident('Karie Le', 'kle5@wisc.edu', 'University of Wisconsin - Madison'))
member_school_presidents.append(MemberSchoolPresident('Henry Tran', 'tranht@uwm.edu', 'University of Wisconsin - Milwaukee'))
# Missing UW - Lacrosse ?? are they even a member school anymore?
# TEST
#member_school_presidents.append(MemberSchoolPresident('Testy Tester', 'tomng2012@gmail.com', 'University of Testing - ayy lmao'))
