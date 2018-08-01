# coding=utf-8

from __future__ import unicode_literals, absolute_import, division, print_function

import time

from sopel import module
from sopel.config.types import StaticSection, ValidatedAttribute

class MuteNoobsSection(StaticSection):
    cooldownTime = ValidatedAttribute('cooldownTime', int, default=120)


def setup(bot):
    bot.config.define_section('mutenoobs', MuteNoobsSection)


def configure(config):
    config.define_section('mutenoobs', MuteNoobsSection, validate=False)
    config.mutenoobs.configure_setting('cooldownTime', 'Seconds to wait until a new user is unmuted')


@module.interval(10)
def check_timeout(bot):
    if bot.memory.contains('mutedNoobs'):
        ts = time.time() - bot.config.mutenoobs.cooldownTime
        # Get list of muted users
        noobList = bot.memory['mutedNoobs']
        # For all entries: Check timeout
        for entry in noobList:
            if entry['joined'] < ts:
                print('Unmuting ' + entry['nick'] + ' @ ' + entry['channel'])
                bot.write(['MODE', entry['channel'], '-q', entry['nick']])
        # Filter expired entries
        bot.memory['mutedNoobs'] = [ entry for entry in noobList if (entry['joined'] >= ts) ]


@module.rule('.*')
@module.event('JOIN')
def user_joined(bot, trigger):
    if trigger.nick != bot.nick:
        # Get (or initialize) list of muted users
        noobList = []
        if bot.memory.contains('mutedNoobs'):
            noobList = bot.memory['mutedNoobs']
        # Add new nick to noobList
        entry = {
            'channel': trigger.sender,
            'nick': trigger.nick,
            'joined': time.time()
            }
        noobList.append(entry)
        bot.memory['mutedNoobs'] = noobList
        # Mute noob
        print('Muting ' + entry['nick'] + ' @ ' + entry['channel'])
        bot.write(['MODE', entry['channel'], '+q', entry['nick']])

@module.commands('foo')
def hello_world(bot, trigger):
    bot.say('Foo? Bar!')
