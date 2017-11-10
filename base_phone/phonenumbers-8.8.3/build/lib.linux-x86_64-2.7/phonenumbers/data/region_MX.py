"""Auto-generated file, do not edit by hand. MX metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_MX = PhoneMetadata(id='MX', country_code=52, international_prefix='0[09]',
    general_desc=PhoneNumberDesc(national_number_pattern='[1-9]\\d{9,10}', possible_length=(10, 11), possible_length_local_only=(7, 8)),
    fixed_line=PhoneNumberDesc(national_number_pattern='(?:33|55|81)\\d{8}|(?:2(?:0[01]|2[1-9]|3[1-35-8]|4[13-9]|7[1-689]|8[1-578]|9[467])|3(?:1[1-79]|[2458][1-9]|7[1-8]|9[1-5])|4(?:1[1-57-9]|[24-6][1-9]|[37][1-8]|8[1-35-9]|9[2-689])|5(?:88|9[1-79])|6(?:1[2-68]|[234][1-9]|5[1-3689]|6[12457-9]|7[1-7]|8[67]|9[4-8])|7(?:[13467][1-9]|2[1-8]|5[13-9]|8[1-69]|9[17])|8(?:2[13-689]|3[1-6]|4[124-6]|6[1246-9]|7[1-378]|9[12479])|9(?:1[346-9]|2[1-4]|3[2-46-8]|5[1348]|[69][1-9]|7[12]|8[1-8]))\\d{7}', example_number='2221234567', possible_length=(10,), possible_length_local_only=(7, 8)),
    mobile=PhoneNumberDesc(national_number_pattern='1(?:(?:33|55|81)\\d{8}|(?:2(?:2[1-9]|3[1-35-8]|4[13-9]|7[1-689]|8[1-578]|9[467])|3(?:1[1-79]|[2458][1-9]|7[1-8]|9[1-5])|4(?:1[1-57-9]|[24-6][1-9]|[37][1-8]|8[1-35-9]|9[2-689])|5(?:88|9[1-79])|6(?:1[2-68]|[2-4][1-9]|5[1-3689]|6[12457-9]|7[1-7]|8[67]|9[4-8])|7(?:[13467][1-9]|2[1-8]|5[13-9]|8[1-69]|9[17])|8(?:2[13-689]|3[1-6]|4[124-6]|6[1246-9]|7[1-378]|9[12479])|9(?:1[346-9]|2[1-4]|3[2-46-8]|5[1348]|[69][1-9]|7[12]|8[1-8]))\\d{7})', example_number='12221234567', possible_length=(11,)),
    toll_free=PhoneNumberDesc(national_number_pattern='8(?:00|88)\\d{7}', example_number='8001234567', possible_length=(10,)),
    premium_rate=PhoneNumberDesc(national_number_pattern='900\\d{7}', example_number='9001234567', possible_length=(10,)),
    shared_cost=PhoneNumberDesc(national_number_pattern='300\\d{7}', example_number='3001234567', possible_length=(10,)),
    personal_number=PhoneNumberDesc(national_number_pattern='500\\d{7}', example_number='5001234567', possible_length=(10,)),
    national_prefix='01',
    national_prefix_for_parsing='0[12]|04[45](\\d{10})',
    national_prefix_transform_rule='1\\1',
    number_format=[NumberFormat(pattern='([358]\\d)(\\d{4})(\\d{4})', format='\\1 \\2 \\3', leading_digits_pattern=['33|55|81'], national_prefix_formatting_rule='01 \\1', national_prefix_optional_when_formatting=True),
        NumberFormat(pattern='(\\d{3})(\\d{3})(\\d{4})', format='\\1 \\2 \\3', leading_digits_pattern=['[2467]|3[0-2457-9]|5[089]|8[02-9]|9[0-35-9]'], national_prefix_formatting_rule='01 \\1', national_prefix_optional_when_formatting=True),
        NumberFormat(pattern='(1)([358]\\d)(\\d{4})(\\d{4})', format='044 \\2 \\3 \\4', leading_digits_pattern=['1(?:33|55|81)'], national_prefix_formatting_rule='\\1', national_prefix_optional_when_formatting=True),
        NumberFormat(pattern='(1)(\\d{3})(\\d{3})(\\d{4})', format='044 \\2 \\3 \\4', leading_digits_pattern=['1(?:[2467]|3[0-2457-9]|5[089]|8[2-9]|9[1-35-9])'], national_prefix_formatting_rule='\\1', national_prefix_optional_when_formatting=True)],
    intl_number_format=[NumberFormat(pattern='([358]\\d)(\\d{4})(\\d{4})', format='\\1 \\2 \\3', leading_digits_pattern=['33|55|81']),
        NumberFormat(pattern='(\\d{3})(\\d{3})(\\d{4})', format='\\1 \\2 \\3', leading_digits_pattern=['[2467]|3[0-2457-9]|5[089]|8[02-9]|9[0-35-9]']),
        NumberFormat(pattern='(1)([358]\\d)(\\d{4})(\\d{4})', format='\\1 \\2 \\3 \\4', leading_digits_pattern=['1(?:33|55|81)']),
        NumberFormat(pattern='(1)(\\d{3})(\\d{3})(\\d{4})', format='\\1 \\2 \\3 \\4', leading_digits_pattern=['1(?:[2467]|3[0-2457-9]|5[089]|8[2-9]|9[1-35-9])'])],
    mobile_number_portable_region=True)
