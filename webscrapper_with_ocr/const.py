
patterns_amazon = {
    'star_rating' : [
        r'([0-5]{1})\s?(?:S|s)tar',
        r'([0-5]{1}\.[0-9])\s?\n?[0-9,]+\s?[R|r]atings',
        r'([0-5]{1}\.?(?:[0-9]+)?)\sout\sof\s[0-5]{1}\s?(?:S|s)tar[s]?',
    ],
    'model_number' : [
        r'[0-9\-]{4}\s[M|m]odel\,?\s?([A-Za-z0-9\-]+)\,?',
        r'(.+)\s[0-9-]{1,2}\s?\-?(?:[L|l]itre|L|l)',
        r'(?:M|m)odel\s?([a-zA-Z0-9\-\s\/]+)\s*?\n(?:[C|c]apacity|[W|w]eighted|[E|e]nergy)',
        # r'[M|m]odel\s?([a-zA-Z0-9\s\-\/\\]+)\n?[M|m]odel\s?[N|n]ame',
        # r'[M|m]odel\s?([a-zA-Z0-9\s\-\/\\]+)\n?[M|m]odel\s?',

    ],
    'model_number_colour_tv' : [
        r'[M|m]odel\s?(?:[N|n]ame|[N|n]umber|)\s?([A-Za-z0-9-]+)',
    ],
    'ee_value' : {
        "AC" : [
            r'ISEER\s?(?:V|v)alue\s?\:\s?([0-5]{1}\.[0-9]+)',
        ],
        "REF" : [
            r'[A|a]nnual\s?[E|e]nergy\s[C|c]onsumption\s?([0-9]+)',
        ],
    },
    'brand_name' : [
        r'[B|b]rand\s?([a-zA-z]+)',
    ],
}

patterns_flipkart = {
    'star_rating' : [
        r'[S|s]tar\s?[R|r]ating\s?\n?([0-5]{1})',
        r'([0-5]{1})\s?(?:S|s)tar',

    ],
    'model_number' : [
        r'[M|m]odel\s?[N|n]ame\s?\n?([A-Za-z0-9\-\s\.]+)\s?\n?(?:[C|c]apacity)',
        # r'[M|m]odel\s?[N|n]ame\s?\n?([A-Za-z0-9\-]+)',

    ],
    'ee_value' : {
        "AC" : [
            r'ISEER\s?(?:V|v)alue\s?\:\s?([0-5]{1}\.[0-9]+)',

        ],
        "REF" : [
            r'[A|a]nnual\s?[E|e]nergy\s[C|c]onsumption\s?([0-9]+)',
        ],
    }
}

patterns_croma = {
    'star_rating': [
            r'([0-5]{1})\s?(?:S|s)tar',
    ],
    'model_number': [
            r'[M|m]odel\s?(?:[N|n]umber|[N|n]ame)\s?\n?([A-Za-z0-9\-\s\.]+)\s?\n?FUNCTIONS',
            r'[M|m]odel\s?(?:[N|n]umber|[N|n]ame)\s?\n?([A-Za-z0-9\-\s\.]+)\s?\n?(?:AIR)\sCONDITIONER\sFEATURES',
            r'[M|m]odel\s?(?:[N|n]umber|[N|n]ame)\s?\n?([A-Za-z0-9\-\s\.]+)\s?\n?FEATURES',
            r'[M|m]odel\s?(?:[N|n]umber|[N|n]ame)\s?\n?([A-Za-z0-9\-\s\.]+)\s?\n?TELEVISION\sSCREEN\sSPECIFICATIONS',
    ],
    'ee_value' : {
        "AC" : [
            r'ISEER\s?(?:V|v)alue\s?\:\s?([0-5]{1}\.[0-9]+)',
        ],
        "REF" : [
            r'[A|a]nnual\s?[E|e]nergy\s[C|c]onsumption\s?([0-9]+)',
        ],
    }
}

columns_based_on_prod = {
    'AC_variable_speed' : ('AC Variable Speed', 12),
    'AC_fixed_speed' : ('AC Fixed Speed', 12),
    'Refrigerator_frost_free' : ('Ref (Frost Free)', 10),
    'Refrigerator_direct_cool' : ('Ref (Direct Cool)', 10),
    'Ceiling_fan' : ('Ceiling Fans.', 12),
    'tabular_florescent_lamps' : ('Tubular Forescent Lamps', 12),
    'LED_lamps' : ('LED lamps', 10),
    'Colour_TV' : ('Colour TV', 9),
    'Electric_water_heater' : ('Electric Water Heater', 10)

}