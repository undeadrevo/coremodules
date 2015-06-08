from util.hook import *
from util import database
import random
import time


__author__ = "cr5315"
#edited by apollojustice to handle duplicate words


# Since DogeXM runs on the same box as SuchModBot, we can load its list of slurs so that they can't be added to the words file
BANNED_WORDS = []
BANNED_WORDS_MODULE = "banned-words"
BOT = None
ENDINGS = [".", "!", "?"]
MODULE = "words"
SLURS = []
WORDS = []


def setup(code):
    global BANNED_WORDS
    global BOT
    global SLURS
    global WORDS
    BOT = code.default

    BANNED_WORDS = database.get(BOT, BANNED_WORDS_MODULE)
    if not BANNED_WORDS:
        BANNED_WORDS = []

    SLURS = database.get("SuchModBot", "slur")
    if not SLURS:
        SLURS = []

    WORDS = database.get(BOT, MODULE)
    if not WORDS:
        WORDS = []


def save_words():
    database.set(BOT, WORDS, MODULE)
    database.set(BOT, BANNED_WORDS, BANNED_WORDS_MODULE)


@hook(cmds=["addword"], args=True, rate=30)
def add_word(code, input):
    try:
        args = input.group(2).split()
        word = args[0].lower()
    except (AttributeError, IndexError):
        return code.reply("Please provide a word")

    for slur in SLURS:
        if slur in word:
            return code.reply("I don't like that word!")

    if word in SLURS:
        return code.reply("I don't like that word!")

    if word in BANNED_WORDS:
        return code.reply("I don't like that word!")

    if len(word) > 10:
        return code.reply("Woah man, that's really long!")

    for w in WORDS:
        if w["word"].strip("\\") == word:
            return code.reply("I already know that word!")

    w = {"word": word, "time": time.time(), "who": input.nick}

    WORDS.append(w.strip("\\"))
    WORDS = list(set(WORDS))
    save_words()
    return code.reply("Added!")


@hook(cmds=["banword"], args=True, admin=True)
def ban_word(code, input):
    global BANNED_WORDS
    try:
        args = input.group(2).split()
        word = args[0].lower()
    except (AttributeError, IndexError):
        return code.reply("Please provide a word")

    delete_word(code, input)

    BANNED_WORDS.append(word.strip("\\"))
    WORDS = list(set(WORDS))
    save_words()
    return code.reply("Word banned.")


@hook(cmds=["unbanword"], args=True, admin=True)
def unban_word(code, input):
    global BANNED_WORDS
    try:
        args = input.group(2).split()
        word = args[0].lower()
    except (AttributeError, IndexError):
        return code.reply("Please provide a word")

    if word in BANNED_WORDS:
        BANNED_WORDS.remove(word)
        WORDS = list(set(WORDS))
        save_words()
        return code.reply("Word unbanned.")
    else:
        return code.reply("That was is not banned.")


@hook(cmds=["deleteword", "delword"], args=True, admin=True, rate=10)
def delete_word(code, input):
    global WORDS
    try:
        args = input.group(2).split()
        word = args[0].lower()
    except (AttributeError, IndexError):
        return code.reply("Please provide a word")

    for w in WORDS:
        if w["word"] == word:
            WORDS.remove(w)
            WORDS = list(set(WORDS))
            save_words()
            return code.reply("Word removed.")

    return code.reply("I don't know that word.")


@hook(cmds=["inspectword"], args=True, admin=True)
def inspect_word(code, input):
    try:
        args = input.group(2).split()
        word = args[0].lower()
    except (AttributeError, IndexError):
        return code.reply("Please provide a word")

    for w in WORDS:
        if w["word"] == word:
            return code.say("%s added by %s on %s" % (w["word"], w["who"], time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(w["time"]))))


@hook(cmds=["words"], rate=15)
def words_cmd(code, input):
    if len(WORDS) == 0:
        return code.reply("I don't know any words!")

    try:
        args = input.group(2).split()
        num = int(args[0])
    except AttributeError:
        num = 5
    except IndexError:
        num = 5
    except ValueError:
        num = 5

    if num > 10:
        num = 10

    unused_words = list(WORDS)

    sentence = []

    for i in xrange(0, num):
        try:
            word = random.choice(unused_words)
            sentence.append(word["word"])
            WORDS = list(set(WORDS))
            unused_words.remove(word)
        except IndexError:
            continue

    return code.say(" ".join(sentence).capitalize() + random.choice(ENDINGS))


@hook(cmds=["wordcount"], rate=15)
def word_count(code, input):
    return code.reply("I know %d words." % len(WORDS))


@hook(cmds=["importwords"], admin=True)
def import_words(code, input):
    """Import words from CodicAI"""
    global WORDS
    try:
        with open("words.txt", "r") as f:
            num = 0
            for line in f.readlines():
                num += 1
                data = line.split("=")
                word = {"time": time.time(), "who": data[0], "word": data[1]}
                WORDS.append(word)

            save_words()
            return code.reply("Added %d words." % num)
    except IOError:
        return code.reply("Unable to find words.txt")