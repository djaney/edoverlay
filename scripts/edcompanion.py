#!/usr/bin/env python3
from screen import Window
from data.journal import JournalWatcher
import pygame
import argparse
import re
from overlays import cards
from data.config import Config, get_config_dir, get_logger_config
from simulator import Simulator
import logging

logging.basicConfig(**get_logger_config())


def main(*args):
    default_dir = get_config_dir()

    parser = argparse.ArgumentParser(description='Show overlay for streaming purposes')
    parser.add_argument('activity', type=str, choices=['exploration', 'race', 'create-race'], default='exploration')
    parser.add_argument('--background', '-b', type=str, default='black', help='background color name (ex. black)')
    parser.add_argument('--size', '-s', type=str, default='720p', help="[width]x[height] or 720p or 1080p")
    parser.add_argument('--dir', '-d', type=str, default=default_dir, help="path to journal directory")
    parser.add_argument('--overlay', '-o', default=False, action='store_true', help="Overlay mode (windows only)")
    parser.add_argument('--config', '-c', type=str, default='', help="config path")
    parser.add_argument('--simulator', type=str, choices=['race', 'exploration'], default=None)
    parser.add_argument('--arg1', type=str, default=None)

    if len(args) == 0:
        args = None

    args = parser.parse_args(args)

    if args.activity == 'race' and args.arg1 is None:
        parser.error('--arg1 must be the race filename')

    journal_path = args.dir

    print('Journal directory: {}'.format(journal_path))

    if args.size == '720p':
        size = (1280, 720)
    elif args.size == '1080p':
        size = (1920, 1080)
    else:
        size_pattern = re.compile("^[0-9]+x[0-9]+$")
        if args.size != '' and size_pattern.match(args.size):
            size = tuple(map(lambda i: int(i), args.size.split("x")))
        else:
            size = None

    win = Window(size=size, is_overlay=args.overlay, color=pygame.Color(args.background))

    watch_list = []
    card_list = []

    if args.config:
        config = Config(config_dir=args.config)
    else:
        config = Config()

    journal = JournalWatcher(
        watch=[],
        directory=journal_path,
        config=config
    )

    if args.activity == 'race':
        config.select_race(args.arg1)

    def append_card(card_class, **kwargs):
        c = card_class(win.screen, journal, **kwargs)
        for w in c.watched():
            watch_list.append(w)
        card_list.append(c)

    if args.activity == 'exploration':
        # exploration card
        append_card(cards.ExplorationCard, position=(0, 1), card_size=(1, 2))
        # current system card
        append_card(cards.CurrentSystemCard, position=(2, 1), text_align='right', card_size=(1, 2))
        # route card
        append_card(cards.RouteCard, position=(0, 0), text_align='left', card_size=(3, 1))

    elif args.activity == 'race':
        if args.overlay:
            append_card(cards.RaceCard, position=(2, 0), card_size=(1, 1))
        else:
            append_card(cards.RaceCard, position=(0, 0), card_size=(3, 3))

    elif args.activity == 'create-race':
        if args.overlay:
            append_card(cards.CreateRaceCard, position=(2, 0), card_size=(1, 1))
        else:
            append_card(cards.CreateRaceCard, position=(0, 0), card_size=(3, 3))
    else:
        raise NotImplementedError("{} not implemented".format(args.activity))

    journal.watch = list(set(watch_list))

    win.screen.fill(win.mask_color)

    sim = None
    if args.simulator:
        sim = SimRunner(Simulator(args.simulator).get_generator())

    while win.loop():

        if sim:
            sim.run()

        journal.refresh()
        win.screen.fill(win.mask_color)
        for card in card_list:
            card.render()

        pygame.display.update()


class SimRunner():
    active = True

    def __init__(self, sim):
        self.sim = sim

    def run(self):
        if self.active:
            self.active = next(self.sim)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(e)
        raise e
