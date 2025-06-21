import re

def extract_classification_markings(text):
    """
    Extract US classification portion markings from text.
    
    Handles both parenthetical (S//SI) and non-parenthetical S//SI formats.
    Returns just the classification marking without parentheses.
    
    Returns a list of all classification markings found in the text.
    """
    
    pattern = r'''
        (?<!\w)                                      # Not preceded by word character
        (?:\()?                                      # Optional opening parenthesis (non-capturing)
        (                                            # Start capture group
            (?:U|C|S|TS)                            # Classification levels
            (?:
                //(?:
                    SI|TK|G|HCS|KDK|ORCON|IMCON|NOFORN|PROPIN|FISA|
                    WINTEL|GAMMA|ECI|NF|PR|FGI|WN|RS|LIMDIS|NODIS|
                    EXDIS|SPECAT|(?:EYES\s+ONLY)|(?:DEA\s+SENSITIVE)|
                    LES|OUO|FOUO|SBU
                )
            )*                                       # Zero or more compartments
            (?:
                //REL\s+TO\s+
                (?:[A-Z]{2,5}(?:\s*,\s*[A-Z]{2,5})*) # Country codes like USA, FVEY, GBR
            )?                                       # Optional releasability
            (?://[A-Z]+)*                           # Additional controls
        )                                            # End capture group
        (?:\))?                                      # Optional closing parenthesis (non-capturing)
        (?!\w)                                       # Not followed by word character
    '''
    
    return re.findall(pattern, text, re.VERBOSE)
