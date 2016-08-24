#!/usr/bin/env python

import os
import commandr
from pogoiv import iv_calculator
import termcolor
from operator import itemgetter

_CALCULATOR = iv_calculator.IvCalculator()
_DB_FILENAME = os.path.expanduser('~/.pgo_db')


class Pokemon(object):

    def __init__(self, name, cp, hp, dust, phrase, strongest_feature, iv_stats, powered_up=False):
        # some hacky shit with unicode female/male symbols
        name = check_nidoran(name)

        self.name = name.title()
        self.cp = int(cp)
        self.hp = int(hp)
        self.dust = int(dust)
        self.phrase = phrase
        self.strongest_feature = strongest_feature
        self.iv_stats = iv_stats
        self.powered_up = bool(powered_up)

    def get_stats(self, verbose=False):
        combinations = _CALCULATOR.get_ivs(
            self.name, self.cp, self.hp, self.dust, self.powered_up)

        if len(combinations) == 1:
            stats = _format_combination(combinations[0])
        else:
            perfections = [c['perfection'] for c in combinations]
            stats = '%s - %s (mean %s of %d)' % (
                _format_perfection(min(perfections)),
                _format_perfection(max(perfections)),
                _format_perfection(sum(perfections) / len(perfections)),
                len(combinations)) 

        phraseCombinations = []
        strongestCombinations = []
        ivStatCombinations = []

        if verbose:
            if self.phrase == 'amazing':
                for i in combinations:
                    if i['perfection'] >= 82.2:
                        phraseCombinations.append(i)
            elif self.phrase == 'strong':
                for i in combinations:
                    if i['perfection'] >= 66.7 and i['perfection'] <= 80:
                        phraseCombinations.append(i)
            elif self.phrase == 'decent':
                for i in combinations:
                    if i['perfection'] >= 51.1 and i['perfection'] <= 64.4:
                        phraseCombinations.append(i)
            elif self.phrase == 'bad':
                for i in combinations:
                    if i['perfection'] <= 48.9:
                        phraseCombinations.append(i)
            elif self.phrase == 'all':
                for i in combinations:
                    phraseCombinations.append(i)

            #now sort if strongest feature
            if self.strongest_feature == 'atk':
                for i in phraseCombinations:
                    if i['atk_iv'] >= i['def_iv'] and i['atk_iv'] >= i['stam_iv']:
                        strongestCombinations.append(i)
            elif self.strongest_feature == 'def':
                for i in phraseCombinations:
                    if i['def_iv'] >= i['atk_iv'] and i['def_iv'] >= i['stam_iv']:
                        strongestCombinations.append(i)
            elif self.strongest_feature == 'stam':
                for i in phraseCombinations:
                    if i['stam_iv'] >= i['atk_iv'] and i['stam_iv'] >= i['def_iv']:
                        strongestCombinations.append(i)      

            # if perfect IV in at least 1 stat
            if self.iv_stats == 'wow':
                for i in strongestCombinations:
                    if i['atk_iv'] == 15 or i['def_iv'] == 15 or i['stam_iv'] == 15:
                        ivStatCombinations.append(i)

            sorted_combinations = sorted(
                ivStatCombinations, key=lambda c: c['perfection'], reverse=True)
            stats += '\n' + '\n'.join(map(_format_combination, sorted_combinations))  
        else:
            sorted_combinations = sorted(
                combinations, key=lambda c: c['perfection'], reverse=True)
            stats += '\n' + '\n'.join(map(_format_combination, sorted_combinations)) 
        
        return '%s, %d/%d/%d, %s: %s' % (
            self.name, self.cp, self.hp, self.dust, self.powered_up, stats)

    def get_record(self):
        return ','.join(map(str, [
            self.name, self.cp, self.hp, self.dust, self.powered_up]))


def check_nidoran(name):
    check = name.lower()
    if check == 'nidoranf':
        female = u'\u2640'.encode('utf-8')
        name = 'Nidoran'+female
    if check == 'nidoranm':
        male = u"\u2642".encode('utf-8')
        name = 'Nidoran' + male

    return name


@commandr.command
def calc(name, cp, hp, dust, phrase='', strongest_feature='', iv_stats='', powered_up=False, verbose=False):
    """Calculates the pokemon's possible IV. Use 
    Phrases:
      - amazing
      - strong
      - decent
      - bad 
      - all
    Strongest feature:
      - atk
      - def
      - stam
    IV stats:
      - wow

    Example:
        python pgo.py calc diglett 71 10 600 amazing def wow -v
    """
    print Pokemon(name, cp, hp, dust, phrase, strongest_feature, iv_stats, powered_up).get_stats(verbose)

@commandr.command('list')
def list_(query=None, verbose=False):
    if query is not None:
        query = query.title()
        query = check_nidoran(query)

    for record in _get_records():
        name, cp, hp, dust, powered_up = record.split(',')
        powered_up = powered_up == 'True'
        if query is None or name == query:
            print Pokemon(name, cp, hp, dust, powered_up).get_stats(verbose)


@commandr.command('sortcp')
def sort_cp_(query=None, verbose=False):
    poke_sorted_by_cp = []
    poke = []

    if query is not None:
        query = query.title()
        query = check_nidoran(query)

    # grabbing the pokes and shoving them into a list of lists (lol)
    for record in _get_records():
        name, cp, hp, dust, powered_up = record.split(',')
        if query is None or name == query:
            poke = [name, int(cp), int(hp), int(dust), powered_up]
            poke_sorted_by_cp.append(poke)

    # sorting by cp
    poke_sorted_by_cp = sorted(poke_sorted_by_cp, key=itemgetter(1), reverse=True)

    # print it out all pretty
    for pokemon in poke_sorted_by_cp:
        name, cp, hp, dust, powered_up = pokemon
        powered_up = powered_up == 'True'
        print Pokemon(name, cp, hp, dust, powered_up).get_stats(verbose)


@commandr.command
def add(name, cp, hp, dust, powered_up=False, verbose=False):
    pokemon = Pokemon(name, cp, hp, dust, powered_up)
    print pokemon.get_stats(verbose)

    record = pokemon.get_record()
    records = _get_records()
    if record in records:
        print 'Already exists'
    else:
        records.append(record)
        _put_records(list(records))
        print 'Added'


@commandr.command
def remove(name, cp, hp, dust, powered_up=False, verbose=False):
    pokemon = Pokemon(name, cp, hp, dust, powered_up)
    print pokemon.get_stats(verbose)

    record = pokemon.get_record()
    records = _get_records()
    if record not in records:
        print 'Does not exist'
    else:
        records.remove(record)
        _put_records(records)
        print 'Removed'


def _format_combination(combination):
    return '%.1f, %d/%d/%d, %s' % (
        combination['level'],
        combination['atk_iv'],
        combination['def_iv'],
        combination['stam_iv'],
        _format_perfection(combination['perfection']))


def _format_perfection(perfection):
    if perfection >= 90:
        color = 'green'
    elif perfection >= 80:
        color = 'yellow'
    else:
        color = 'red'

    return termcolor.colored('%.2f%%' % perfection, color)


def _get_records():
    with open(_DB_FILENAME, 'r') as db_file:
        return db_file.read().splitlines()


def _put_records(records):
    with open(_DB_FILENAME, 'w') as db_file:
        db_file.write('\n'.join(records) + '\n')


if __name__ == '__main__':
    commandr.Run()
