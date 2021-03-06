# All static variables should be declared and initialized in this file.
# Since each conference from year to year will have different prices, dates, etc -- make sure you
# go in here and change the variables accordingly

# TODO Don't forget to remove fake school below

import datetime


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
    REGULAR_REG_CAP = 175
    ALUMNI_REG_CAP = 25     # Soft-cap. An additional 5 spots are being reserved for Alumni, to be distributed manually
    STAFF_REG_CAP = 83


class HotelPaymentTypes:
    SINGLE_SPOT = 'single_spot'
    WHOLE_ROOM = 'whole_room'


# Make sure these strings match the strings in code_types
class CodeTypes:
    WAITLIST_REG = 'Waitlist Registration'
    REGULAR_REG = 'Regular Registration'
    STAFF_REG = 'Staff Registration'
    BANQUET = 'Banquet Only'
    FAMILY_LEADER = 'Family Leader'
    SPECIAL = 'Special'


code_types = ['Waitlist Registration', 'Regular Registration', 'Staff Registration', 'Banquet Only', 'Family Leader', 'Special']


methods_of_payment = ['PayPal', 'PayPal (Bulk)', 'Venmo', 'Scholarship', 'Other']


# Open 12-14-2017 @ 1800/6:00p CENTRAL (timezone is set in settings.py)
# Close 1-3-2018 @ 11:59:59
early_reg_open_date = datetime.datetime(2017, 12, 14, 18, 0, 0)
early_reg_close_date = datetime.datetime(2018, 1, 3, 23, 59, 59)

# Open 1-4-2018 @ 6:00p CENTRAL
# Close 1-18-2018 @ 11:59p
regular_reg_open_date = datetime.datetime(2018, 1, 4, 18, 0, 0)
regular_reg_close_date = datetime.datetime(2018, 1, 18, 23, 59, 59)

# Open 1-4-2017 @ 6:00p CENTRAL
# Close 2-14-2018 @ 11:59p
alumni_reg_open_date = datetime.datetime(2018, 1, 4, 18, 0, 0)
alumni_reg_close_date = datetime.datetime(2018, 2, 14, 23, 59, 59)


payment_refund_deadline = datetime.datetime(2018, 2, 14, 23, 59, 59)
staff_payment_deadline = datetime.datetime(2018, 2, 7, 23, 59, 59)

roommate_deadline = datetime.datetime(2018, 3, 1, 23, 59, 59)

# these are dummy dates -- replace with real ones soon
workshop_release_date = datetime.datetime(2018, 3, 12, 18, 0, 0)
workshop_deadline = datetime.datetime(2018, 3, 19, 23, 59, 59)

graduation_years = [
    2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023,
    2024, 2025]


default_pronouns = [
    'He, Him, His',
    'She, Her, Hers',
    'They, Them, Theirs'
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


class FamilyLeader(object):
    def __init__(self, first_name, last_name, family_id, family_name, photo_name, animation_delay):
        self.first_name = first_name
        self.last_name = last_name
        self.family_id = family_id
        self.family_name = family_name
        self.photo_name = photo_name
        self.animation_delay = animation_delay


class FamilyMember(object):
    def __init__(self, first_name, last_name, pronouns, school, major, facebook, instagram, twitter, snapchat, linkedin, photo_name, animation_delay):
        self.first_name = first_name
        self.last_name = last_name
        self.pronouns = pronouns
        self.school = school
        self.major = major
        self.facebook = facebook
        self.instagram = instagram
        self.twitter = twitter
        self.snapchat = snapchat
        self.linkedin = linkedin
        self.photo_name = photo_name
        self.animation_delay = animation_delay
