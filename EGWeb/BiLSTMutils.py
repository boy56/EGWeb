import logging, sys, argparse


def str2bool(v):
    # copy from StackOverflow
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_entity(tag_seq, char_seq):
    VERB = get_VERB_entity(tag_seq, char_seq)
    NOUN = get_NOUN_entity(tag_seq, char_seq)
    return VERB, NOUN


def get_VERB_entity(tag_seq, char_seq):
    length = len(char_seq)
    VERB = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-VERB':
            if 'verb' in locals().keys():
                VERB.append(verb)
                del verb
            verb = char
            if i+1 == length:
                VERB.append(verb)
        if tag == 'I-VERB':
            verb += char
            if i+1 == length:
                VERB.append(verb)
        if tag not in ['I-VERB', 'B-VERB']:
            if 'verb' in locals().keys():
                VERB.append(verb)
                del verb
            continue
    return VERB


def get_NOUN_entity(tag_seq, char_seq):
    length = len(char_seq)
    NOUN = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-NOUN':
            if 'noun' in locals().keys():
                NOUN.append(noun)
                del noun
            noun = char
            if i+1 == length:
                NOUN.append(noun)
        if tag == 'I-NOUN':
            noun += char
            if i+1 == length:
                NOUN.append(noun)
        if tag not in ['I-NOUN', 'B-NOUN']:
            if 'noun' in locals().keys():
                NOUN.append(noun)
                del noun
            continue
    return NOUN

